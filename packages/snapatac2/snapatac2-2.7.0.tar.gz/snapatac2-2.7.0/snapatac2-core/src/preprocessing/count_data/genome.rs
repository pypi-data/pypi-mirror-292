//! # Genomic Feature Counter Module
//!
//! This module provides the functionality to count genomic features (such as genes or transcripts) 
//! in genomic data. The primary structures in this module are `TranscriptCount` and `GeneCount`, 
//! both of which implement the `FeatureCounter` trait. The `FeatureCounter` trait provides a 
//! common interface for handling feature counts, including methods for resetting counts, 
//! updating counts, and retrieving feature IDs, names, and counts.
//!
//! `SparseCoverage`, from the bed_utils crate, is used for maintaining counts of genomic features, 
//! and this structure also implements the `FeatureCounter` trait in this module.
//!
//! `TranscriptCount` and `GeneCount` structures also hold a reference to `Promoters`, which 
//! provides additional information about the genomic features being counted.
//!
//! To handle the mapping of gene names to indices, an `IndexMap` is used in the `GeneCount` structure. 
//! This allows for efficient look-up of gene indices by name, which is useful when summarizing counts 
//! at the gene level.
//!
//! The module aims to provide a comprehensive, efficient, and flexible way to handle and manipulate 
//! genomic feature counts in Rust.
use noodles::{core::Position, gff, gff::record::Strand, gtf};
use bed_utils::bed::tree::GenomeRegions;
use anyhow::{Result, bail};
use std::{collections::{BTreeMap, HashMap}, fmt::Debug, io::BufRead};
use indexmap::map::IndexMap;
use bed_utils::bed::{GenomicRange, BEDLike, tree::SparseCoverage};
use itertools::Itertools;
use num::traits::{ToPrimitive, NumCast};
use anndata::data::utils::to_csr_data;
use bed_utils::bed::BedGraph;
use indexmap::IndexSet;
use polars::frame::DataFrame;
use nalgebra_sparse::CsrMatrix;
use polars::prelude::{NamedFrom, Series};
use rayon::iter::{IntoParallelIterator, ParallelIterator};
use std::ops::Range;

use super::{qc::Fragment, CountingStrategy};

/// Position is 1-based.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Transcript {
    pub transcript_name: Option<String>,
    pub transcript_id: String,
    pub gene_name: String,
    pub gene_id: String,
    pub is_coding: Option<bool>,
    pub chrom: String,
    pub left: Position,
    pub right: Position,
    pub strand: Strand,
}

pub struct TranscriptParserOptions {
    pub transcript_name_key: String,
    pub transcript_id_key: String,
    pub gene_name_key: String,
    pub gene_id_key: String,
}

impl<'a> Default for TranscriptParserOptions {
    fn default() -> Self {
        Self {
            transcript_name_key: "transcript_name".to_string(),
            transcript_id_key: "transcript_id".to_string(),
            gene_name_key: "gene_name".to_string(),
            gene_id_key: "gene_id".to_string(),
        }
    }
}

fn from_gtf(record: gtf::Record, options: &TranscriptParserOptions) -> Result<Transcript> {
    if record.ty() != "transcript" {
        bail!("record is not a transcript");
    }

    let left = record.start();
    let right = record.end();
    let attributes: HashMap<&str, &str> = record
        .attributes()
        .iter()
        .map(|x| (x.key(), x.value()))
        .collect();
    let get_attr = |key: &str| -> String { 
        attributes.get(key).expect(&format!("failed to find '{}' in record: {}", key, record)) .to_string()
    };

    Ok(Transcript {
        transcript_name: attributes.get(options.transcript_name_key.as_str()).map(|x| x.to_string()),
        transcript_id: get_attr(options.transcript_id_key.as_str()),
        gene_name: get_attr(options.gene_name_key.as_str()),
        gene_id: get_attr(options.gene_id_key.as_str()),
        is_coding: attributes
            .get("transcript_type")
            .map(|x| *x == "protein_coding"),
        chrom: record.reference_sequence_name().to_string(),
        left,
        right,
        strand: match record.strand() {
            None => Strand::None,
            Some(gtf::record::Strand::Forward) => Strand::Forward,
            Some(gtf::record::Strand::Reverse) => Strand::Reverse,
        },
    })
}

fn from_gff(record: gff::Record, options: &TranscriptParserOptions) -> Result<Transcript> {
    if record.ty() != "transcript" {
        bail!("record is not a transcript");
    }

    let left = record.start();
    let right = record.end();
    let attributes = record.attributes();
    let get_attr = |key: &str| -> String { 
        attributes.get(key).expect(&format!("failed to find '{}' in record: {}", key, record)) .to_string()
    };

    Ok(Transcript {
        transcript_name: attributes.get(options.transcript_name_key.as_str()).map(|x| x.to_string()),
        transcript_id: get_attr(options.transcript_id_key.as_str()),
        gene_name: get_attr(options.gene_name_key.as_str()),
        gene_id: get_attr(options.gene_id_key.as_str()),
        is_coding: attributes
            .get("transcript_type")
            .map(|x| x.as_string() == Some("protein_coding")),
        chrom: record.reference_sequence_name().to_string(),
        left,
        right,
        strand: record.strand(),
    })
}

impl Transcript {
    pub fn get_tss(&self) -> Option<usize> {
        match self.strand {
            Strand::Forward => Some(<Position as TryInto<usize>>::try_into(self.left).unwrap() - 1),
            Strand::Reverse => {
                Some(<Position as TryInto<usize>>::try_into(self.right).unwrap() - 1)
            }
            _ => None,
        }
    }
}

pub fn read_transcripts_from_gtf<R>(input: R, options: &TranscriptParserOptions) -> Result<Vec<Transcript>>
where
    R: BufRead,
{
    gtf::Reader::new(input)
        .records()
        .try_fold(Vec::new(), |mut acc, rec| {
            if let Ok(transcript) = from_gtf(rec?, options) {
                acc.push(transcript);
            }
            Ok(acc)
        })
}

pub fn read_transcripts_from_gff<R>(input: R, options: &TranscriptParserOptions) -> Result<Vec<Transcript>>
where
    R: BufRead,
{
    gff::Reader::new(input)
        .records()
        .try_fold(Vec::new(), |mut acc, rec| {
            if let Ok(transcript) = from_gff(rec?, options) {
                acc.push(transcript);
            }
            Ok(acc)
        })
}

pub struct Promoters {
    pub regions: GenomeRegions<GenomicRange>,
    pub transcripts: Vec<Transcript>,
}

impl Promoters {
    pub fn new(
        transcripts: Vec<Transcript>,
        upstream: u64,
        downstream: u64,
        include_gene_body: bool,
    ) -> Self {
        let regions = transcripts
            .iter()
            .map(|transcript| {
                let left =
                    (<Position as TryInto<usize>>::try_into(transcript.left).unwrap() - 1) as u64;
                let right =
                    (<Position as TryInto<usize>>::try_into(transcript.right).unwrap() - 1) as u64;
                let (start, end) = match transcript.strand {
                    Strand::Forward => (
                        left.saturating_sub(upstream),
                        downstream + (if include_gene_body { right } else { left }),
                    ),
                    Strand::Reverse => (
                        (if include_gene_body { left } else { right }).saturating_sub(downstream),
                        right + upstream,
                    ),
                    _ => panic!("Miss strand information for {}", transcript.transcript_id),
                };
                GenomicRange::new(transcript.chrom.clone(), start, end)
            })
            .collect();
        Promoters {
            regions,
            transcripts,
        }
    }
}


/// `FeatureCounter` is a trait that provides an interface for counting genomic features.
/// Types implementing `FeatureCounter` can store feature counts and provide several 
/// methods for manipulating and retrieving those counts.
pub trait FeatureCounter {
    type Value;

    /// Returns the total number of distinct features counted.
    fn num_features(&self) -> usize { self.get_feature_ids().len() }

    /// Resets the counter for all features.
    fn reset(&mut self);

    /// Updates the counter according to the given region and count.
    fn insert<B: BEDLike, N: ToPrimitive + Copy>(&mut self, tag: &B, count: N);

    /// Updates the counter according to the given fragment
    fn insert_fragment(&mut self, tag: &Fragment, strategy: &CountingStrategy);

    /// Returns a vector of feature ids.
    fn get_feature_ids(&self) -> Vec<String>;

    /// Returns a vector of feature names if available.
    fn get_feature_names(&self) -> Option<Vec<String>> { None }

    /// Returns a vector of tuples, each containing a feature's index and its count.
    fn get_counts(&self) -> Vec<(usize, Self::Value)>;
}

/// Implementation of `FeatureCounter` trait for `SparseCoverage` struct.
/// `SparseCoverage` represents a sparse coverage map for genomic data.
impl<D: BEDLike> FeatureCounter for SparseCoverage<'_, D, u32> {
    type Value = u32;

    fn reset(&mut self) { self.reset(); }

    fn insert<B: BEDLike, N: ToPrimitive + Copy>(&mut self, tag: &B, count: N) {
        self.insert(tag, <u32 as NumCast>::from(count).unwrap());
    }

    fn insert_fragment(&mut self, tag: &Fragment, strategy: &CountingStrategy) {
        if tag.is_single() {
            tag.to_insertions().iter().for_each(|x| {
                self.insert(x, 1);
            });
        } else {
            match strategy {
                CountingStrategy::Fragment => {
                    self.insert(tag, 1);
                },
                CountingStrategy::Insertion => {
                    tag.to_insertions().iter().for_each(|x| {
                        self.insert(x, 1);
                    });
                },
                CountingStrategy::PIC => {
                    tag.to_insertions().into_iter()
                        .flat_map(|x| self.get_index(&x))
                        .unique().collect::<Vec<_>>().into_iter().for_each(|i| {
                            self.insert_at_index::<u32>(i, 1);
                        });
                }
            }
        }
    }

    fn get_feature_ids(&self) -> Vec<String> {
        self.get_regions().map(|x| x.to_genomic_range().pretty_show()).collect()
    }

    fn get_counts(&self) -> Vec<(usize, Self::Value)> {
        self.get_coverage().iter().map(|(k, v)| (*k, *v)).collect()
    }
}

/// `TranscriptCount` is a struct that represents the count of genomic features at the transcript level.
/// It holds a `SparseCoverage` counter and a reference to `Promoters`.
#[derive(Clone)]
pub struct TranscriptCount<'a> {
    counter: SparseCoverage<'a, GenomicRange, u32>,
    promoters: &'a Promoters,
}

impl<'a> TranscriptCount<'a> {
    pub fn new(promoters: &'a Promoters) -> Self {
        Self {
            counter: SparseCoverage::new(&promoters.regions),
            promoters,
        }
    }

    pub fn gene_names(&self) -> Vec<String> {
        self.promoters
            .transcripts
            .iter()
            .map(|x| x.gene_name.clone())
            .collect()
    }
}

/// `GeneCount` is a struct that represents the count of genomic features at the gene level.
/// It holds a `TranscriptCount` counter and a map from gene names to their indices.
#[derive(Clone)]
pub struct GeneCount<'a> {
    counter: TranscriptCount<'a>,
    gene_name_to_idx: IndexMap<&'a str, usize>,
}

/// Implementation of `GeneCount`
impl<'a> GeneCount<'a> {
    pub fn new(counter: TranscriptCount<'a>) -> Self {
        let gene_name_to_idx: IndexMap<_, _> = counter
            .promoters
            .transcripts
            .iter()
            .map(|x| x.gene_name.as_str())
            .unique()
            .enumerate()
            .map(|(a, b)| (b, a))
            .collect();
        Self {
            counter,
            gene_name_to_idx,
        }
    }
}

/// Implementations of `FeatureCounter` trait for `TranscriptCount` and `GeneCount` structs.
impl FeatureCounter for TranscriptCount<'_> {
    type Value = u32;

    fn reset(&mut self) { self.counter.reset(); }

    fn insert<B: BEDLike, N: ToPrimitive + Copy>(&mut self, tag: &B, count: N) {
        self.counter.insert(tag, <u32 as NumCast>::from(count).unwrap());
    }

    fn insert_fragment(&mut self, tag: &Fragment, strategy: &CountingStrategy) {
        self.counter.insert_fragment(tag, strategy);
    }

    fn get_feature_ids(&self) -> Vec<String> {
        self.promoters.transcripts.iter().map(|x| x.transcript_id.clone()).collect()
    }

    fn get_counts(&self) -> Vec<(usize, Self::Value)> {
        self.counter.get_counts()
    }
}

impl FeatureCounter for GeneCount<'_> {
    type Value = u32;

    fn reset(&mut self) { self.counter.reset(); }

    fn insert<B: BEDLike, N: ToPrimitive + Copy>(&mut self, tag: &B, count: N) {
        self.counter.insert(tag, <u32 as NumCast>::from(count).unwrap());
    }

    fn insert_fragment(&mut self, tag: &Fragment, strategy: &CountingStrategy) {
        self.counter.insert_fragment(tag, strategy);
    }

    fn get_feature_ids(&self) -> Vec<String> {
        self.gene_name_to_idx.keys().map(|x| x.to_string()).collect()
    }

    fn get_counts(&self) -> Vec<(usize, Self::Value)> {
        let mut counts = BTreeMap::new();
        self.counter.get_counts().into_iter().for_each(|(k, v)| {
            let idx = *self.gene_name_to_idx.get(
                self.counter.promoters.transcripts[k].gene_name.as_str()
            ).unwrap();
            let current_v = counts.entry(idx).or_insert(v);
            if *current_v < v { *current_v = v }
        });
        counts.into_iter().collect()
    }
}

#[derive(Debug, Clone, Eq, PartialEq)]
pub struct ChromSizes(IndexMap<String, u64>);

impl ChromSizes {
    pub fn total_size(&self) -> u64 {
        self.0.iter().map(|x| x.1).sum()
    }

    pub fn get(&self, chrom: &str) -> Option<u64> {
        self.0.get(chrom).copied()
    }

    pub fn to_dataframe(&self) -> DataFrame {
        DataFrame::new(vec![
            Series::new(
                "reference_seq_name",
                self.0.iter().map(|x| x.0.clone()).collect::<Series>(),
            ),
            Series::new(
                "reference_seq_length",
                self.0.iter().map(|x| x.1).collect::<Series>(),
            ),
        ])
        .unwrap()
    }
}

impl<S> FromIterator<(S, u64)> for ChromSizes
where
    S: Into<String>,
{
    fn from_iter<T: IntoIterator<Item = (S, u64)>>(iter: T) -> Self {
        ChromSizes(iter.into_iter().map(|(s, l)| (s.into(), l)).collect())
    }
}

impl<'a> IntoIterator for &'a ChromSizes {
    type Item = (&'a String, &'a u64);
    type IntoIter = indexmap::map::Iter<'a, String, u64>;

    fn into_iter(self) -> Self::IntoIter {
        self.0.iter()
    }
}

impl IntoIterator for ChromSizes {
    type Item = (String, u64);
    type IntoIter = indexmap::map::IntoIter<String, u64>;

    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}

/// 0-based index that maps genomic loci to integers.
#[derive(Debug, Clone)]
pub struct GenomeBaseIndex {
    pub(crate) chroms: IndexSet<String>,
    pub(crate) base_accum_len: Vec<u64>,
    pub(crate) binned_accum_len: Vec<u64>,
    pub(crate) step: usize,
}

impl GenomeBaseIndex {
    pub fn new(chrom_sizes: &ChromSizes) -> Self {
        let mut acc = 0;
        let base_accum_len = chrom_sizes
            .0
            .iter()
            .map(|(_, length)| {
                acc += length;
                acc
            })
            .collect::<Vec<_>>();
        Self {
            chroms: chrom_sizes.0.iter().map(|x| x.0.clone()).collect(),
            binned_accum_len: base_accum_len.clone(),
            base_accum_len,
            step: 1,
        }
    }

    /// Retreive the range of a chromosome.
    pub fn get_range(&self, chr: &str) -> Option<Range<usize>> {
        let i = self.chroms.get_index_of(chr)?;
        let end = self.binned_accum_len[i];
        let start = if i == 0 {
            0
        } else {
            self.binned_accum_len[i - 1]
        };
        Some(start as usize..end as usize)
    }

    pub fn to_index(&self) -> anndata::data::index::Index {
        self.chrom_sizes()
            .map(|(chrom, length)| {
                let i = anndata::data::index::Interval {
                    start: 0,
                    end: length as usize,
                    size: self.step,
                    step: self.step,
                };
                (chrom.to_owned(), i)
            })
            .collect()
    }

    /// Number of indices.
    pub fn len(&self) -> usize {
        self.binned_accum_len
            .last()
            .map(|x| *x as usize)
            .unwrap_or(0)
    }

    pub fn chrom_sizes(&self) -> impl Iterator<Item = (&String, u64)> + '_ {
        let mut prev = 0;
        self.chroms
            .iter()
            .zip(self.base_accum_len.iter())
            .map(move |(chrom, acc)| {
                let length = acc - prev;
                prev = *acc;
                (chrom, length)
            })
    }

    /// Check if the index contains the given chromosome.
    pub fn contain_chrom(&self, chrom: &str) -> bool {
        self.chroms.contains(chrom)
    }

    pub fn with_step(&self, s: usize) -> Self {
        let mut prev = 0;
        let mut acc_low_res = 0;
        let binned_accum_len = self.base_accum_len.iter().map(|acc| {
            let length = acc - prev;
            prev = *acc;
            acc_low_res += num::Integer::div_ceil(&length, &(s as u64));
            acc_low_res
        }).collect();
        Self {
            chroms: self.chroms.clone(),
            base_accum_len: self.base_accum_len.clone(),
            binned_accum_len,
            step: s,
        }
    }

    /// Given a genomic position, return the corresponding index.
    pub fn get_position_rev(&self, chrom: &str, pos: u64) -> usize {
        let i = self.chroms.get_index_of(chrom).expect(format!("Chromosome {} not found", chrom).as_str());
        let size = if i == 0 {
            self.base_accum_len[i]
        } else {
            self.base_accum_len[i] - self.base_accum_len[i - 1]
        };
        if pos as u64 >= size {
            panic!("Position {} is out of range for chromosome {}", pos, chrom);
        }
        let pos = (pos as usize) / self.step;
        if i == 0 {
            pos
        } else {
            self.binned_accum_len[i - 1] as usize + pos
        }
    }

    /// O(log(N)). Given a index, find the corresponding chromosome.
    pub fn get_chrom(&self, pos: usize) -> &String {
        let i = pos as u64;
        let j = match self.binned_accum_len.binary_search(&i) {
            Ok(j) => j + 1,
            Err(j) => j,
        };
        self.chroms.get_index(j).unwrap()
    }

    /// O(log(N)). Given a index, find the corresponding chromosome and position.
    pub fn get_position(&self, pos: usize) -> (&String, u64) {
        let i = pos as u64;
        match self.binned_accum_len.binary_search(&i) {
            Ok(j) => (self.chroms.get_index(j + 1).unwrap(), 0),
            Err(j) => {
                let chr = self.chroms.get_index(j).unwrap();
                let prev = if j == 0 {
                    0
                } else {
                    self.binned_accum_len[j - 1]
                };
                let start = (i - prev) * self.step as u64;
                (chr, start)
            }
        }
    }

    /// O(log(N)). Given a index, find the corresponding chromosome and position.
    pub fn get_region(&self, pos: usize) -> GenomicRange {
        let i = pos as u64;
        match self.binned_accum_len.binary_search(&i) {
            Ok(j) => {
                let chr = self.chroms.get_index(j + 1).unwrap();
                let acc = self.base_accum_len[j + 1];
                let size = acc - self.base_accum_len[j];
                let start = 0;
                let end = (start + self.step as u64).min(size);
                GenomicRange::new(chr, start, end)
            }
            Err(j) => {
                let chr = self.chroms.get_index(j).unwrap();
                let acc = self.base_accum_len[j];
                let size = if j == 0 {
                    acc
                } else {
                    acc - self.base_accum_len[j - 1]
                };
                let prev = if j == 0 {
                    0
                } else {
                    self.binned_accum_len[j - 1]
                };
                let start = (i - prev) * self.step as u64;
                let end = (start + self.step as u64).min(size);
                GenomicRange::new(chr, start, end)
            }
        }
    }

    // Given a base index, find the corresponding index in the downsampled matrix.
    pub(crate) fn get_coarsed_position(&self, pos: usize) -> usize {
        if self.step <= 1 {
            pos
        } else {
            let i = pos as u64;
            match self.base_accum_len.binary_search(&i) {
                Ok(j) => self.binned_accum_len[j] as usize,
                Err(j) => {
                    let (acc, acc_low_res) = if j == 0 {
                        (0, 0)
                    } else {
                        (self.base_accum_len[j - 1], self.binned_accum_len[j - 1])
                    };
                    (acc_low_res + (i - acc) / self.step as u64) as usize
                }
            }
        }
    }
}

/// `ChromValues` is a type alias for a vector of `BedGraph<N>` objects.
/// Each `BedGraph` instance represents a genomic region along with a
/// numerical value (like coverage or score).
pub type ChromValues<N> = Vec<BedGraph<N>>;

/// `ChromValueIter` represents an iterator over the chromosome values.
/// Each item in the iterator is a tuple of a vector of `ChromValues<N>` objects,
/// a start index, and an end index.
pub struct ChromValueIter<I> {
    pub(crate) iter: I,
    pub(crate) regions: Vec<GenomicRange>,
    pub(crate) length: usize,
}

impl<'a, I, T> ChromValueIter<I>
where
    I: ExactSizeIterator<Item = (CsrMatrix<T>, usize, usize)> + 'a,
    T: Copy,
{
    /// Aggregate the values in the iterator by the given `FeatureCounter`.
    pub fn aggregate_by<C>(
        self,
        mut counter: C,
    ) -> impl ExactSizeIterator<Item = (CsrMatrix<T>, usize, usize)>
    where
        C: FeatureCounter<Value = T> + Clone + Sync,
        T: Sync + Send + num::ToPrimitive,
    {
        let n_col = counter.num_features();
        counter.reset();
        self.iter.map(move |(mat, i, j)| {
            let n = j - i;
            let vec = (0..n)
                .into_par_iter()
                .map(|k| {
                    let row = mat.get_row(k).unwrap();
                    let mut coverage = counter.clone();
                    row.col_indices()
                        .into_iter()
                        .zip(row.values())
                        .for_each(|(idx, val)| {
                            coverage.insert(&self.regions[*idx], *val);
                        });
                    coverage.get_counts()
                })
                .collect::<Vec<_>>();
            let (r, c, offset, ind, data) = to_csr_data(vec, n_col);
            (CsrMatrix::try_from_csr_data(r,c,offset,ind, data).unwrap(), i, j)
        })
    }
}

impl<I, T> Iterator for ChromValueIter<I>
where
    I: Iterator<Item = (CsrMatrix<T>, usize, usize)>,
    T: Copy,
{
    type Item = (Vec<ChromValues<T>>, usize, usize);

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|(x, start, end)| {
            let values = x
                .row_iter()
                .map(|row| {
                    row.col_indices()
                        .iter()
                        .zip(row.values())
                        .map(|(i, v)| BedGraph::from_bed(&self.regions[*i], *v))
                        .collect()
                })
                .collect();
            (values, start, end)
        })
    }
}

impl<I, T> ExactSizeIterator for ChromValueIter<I>
where
    I: Iterator<Item = (CsrMatrix<T>, usize, usize)>,
    T: Copy,
{
    fn len(&self) -> usize {
        self.length
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use bed_utils::bed::BEDLike;
    use std::str::FromStr;

    #[test]
    fn test_index1() {
        let chrom_sizes = vec![
            ("1".to_owned(), 13),
            ("2".to_owned(), 71),
            ("3".to_owned(), 100),
        ].into_iter().collect();
        let mut index = GenomeBaseIndex::new(&chrom_sizes);

        assert_eq!(index.get_range("1").unwrap(), 0..13);
        assert_eq!(index.get_range("2").unwrap(), 13..84);
        assert_eq!(index.get_range("3").unwrap(), 84..184);

        assert_eq!(
            chrom_sizes.clone(),
            index
                .chrom_sizes()
                .map(|(a, b)| (a.to_owned(), b))
                .collect()
        );

        [
            (0, "1:0-1"),
            (12, "1:12-13"),
            (13, "2:0-1"),
            (100, "3:16-17"),
        ]
        .into_iter()
        .for_each(|(i, txt)| {
            let locus = GenomicRange::from_str(txt).unwrap();
            assert_eq!(index.get_region(i), locus);
            assert_eq!(index.get_position_rev(locus.chrom(), locus.start()), i);
        });

        index = index.with_step(2);
        [(0, "1:0-2"), (6, "1:12-13"), (7, "2:0-2"), (11, "2:8-10")]
            .into_iter()
            .for_each(|(i, txt)| {
                let locus = GenomicRange::from_str(txt).unwrap();
                assert_eq!(index.get_region(i), locus);
                assert_eq!(index.get_position_rev(locus.chrom(), locus.start()), i);
            });

        index = index.with_step(3);
        [
            (0, "1:0-3"),
            (2, "1:6-9"),
            (4, "1:12-13"),
            (5, "2:0-3"),
            (29, "3:0-3"),
            (62, "3:99-100"),
        ]
        .into_iter()
        .for_each(|(i, txt)| {
            let locus = GenomicRange::from_str(txt).unwrap();
            assert_eq!(index.get_region(i), locus);
            assert_eq!(index.get_position_rev(locus.chrom(), locus.start()), i);
        });
    }

    #[test]
    fn test_index2() {
        let chrom_sizes = vec![
            ("1".to_owned(), 13),
            ("2".to_owned(), 71),
            ("3".to_owned(), 100),
        ].into_iter().collect();

        let index = GenomeBaseIndex::new(&chrom_sizes);
        [(0, 0), (12, 12), (13, 13), (100, 100)]
            .into_iter()
            .for_each(|(i, i_)| assert_eq!(index.get_coarsed_position(i), i_));

        let index2 = index.with_step(2);
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (3, 1),
            (4, 2),
            (5, 2),
            (6, 3),
            (7, 3),
            (8, 4),
            (9, 4),
            (10, 5),
            (11, 5),
            (12, 6),
            (13, 7),
            (14, 7),
            (15, 8),
        ]
        .into_iter()
        .for_each(|(i1, i2)| {
            assert_eq!(index2.get_coarsed_position(i1), i2);
            let locus = index.get_region(i1);
            assert_eq!(index2.get_position_rev(locus.chrom(), locus.start()), i2);
        });
    }

    #[test]
    fn test_read_transcript() {
        let gff = "chr1\tHAVANA\tgene\t11869\t14409\t.\t+\t.\tgene_id=ENSG00000223972.5;gene_type=transcribed_unprocessed_pseudogene;gene_name=DDX11L1;level=2;hgnc_id=HGNC:37102;havana_gene=OTTHUMG00000000961.2\n\
                     chr1\tHAVANA\ttranscript\t11869\t14409\t.\t+\t.\tgene_id=ENSG00000223972.5;transcript_id=ENST00000456328.2;gene_type=transcribed_unprocessed_pseudogene;gene_name=DDX11L1;transcript_type=processed_transcript;transcript_name=DDX11L1-202;level=2;transcript_support_level=1\n\
                     chr1\tHAVANA\texon\t11869\t12227\t.\t+\t.\tgene_id=ENSG00000223972.5;transcript_id=ENST00000456328.2;gene_type=transcribed_unprocessed_pseudogene;gene_name=DDX11L1;transcript_type=processed_transcript;transcript_name=DDX11L1-202;exon_number=1\n\
                     chr1\tHAVANA\texon\t12613\t12721\t.\t+\t.\tgene_id=ENSG00000223972.5;transcript_id=ENST00000456328.2;gene_type=transcribed_unprocessed_pseudogene;gene_name=DDX11L1;transcript_type=processed_transcript;transcript_name=DDX11L1-202;exon_number=2\n\
                     chr1\tHAVANA\texon\t13221\t14409\t.\t+\t.\tgene_id=ENSG00000223972.5;transcript_id=ENST00000456328.2;gene_type=transcribed_unprocessed_pseudogene;gene_name=DDX11L1;transcript_type=processed_transcript;transcript_name=DDX11L1-202;exon_number=3";

        let gtf = "chr1\tHAVANA\tgene\t11869\t14409\t.\t+\t.\tgene_id \"ENSG00000223972.5\"; gene_type \"transcribed_unprocessed_pseudogene\"; gene_name \"DDX11L1\"; level 2; hgnc_id \"HGNC:37102\"; havana_gene \"OTTHUMG00000000961.2\";\n\
            chr1\tHAVANA\ttranscript\t11869\t14409\t.\t+\t.\tgene_id \"ENSG00000223972.5\"; transcript_id \"ENST00000456328.2\"; gene_type \"transcribed_unprocessed_pseudogene\"; gene_name \"DDX11L1\"; transcript_type \"processed_transcript\"; transcript_name \"DDX11L1-202\"; level 2; transcript_support_level \"1\"; hgnc_id \"HGNC:37102\"; tag \"basic\"; havana_gene \"OTTHUMG00000000961.2\"; havana_transcript \"OTTHUMT00000362751.1\";\n\
            chr1\tHAVANA\texon\t11869\t12227\t.\t+\t.\tgene_id \"ENSG00000223972.5\"; transcript_id \"ENST00000456328.2\"; gene_type \"transcribed_unprocessed_pseudogene\"; gene_name \"DDX11L1\"; transcript_type \"processed_transcript\"; transcript_name \"DDX11L1-202\"; exon_number 1; exon_id \"ENSE00002234944.1\"; level 2; transcript_support_level \"1\"; hgnc_id \"HGNC:37102\"; tag \"basic\"; havana_gene \"OTTHUMG00000000961.2\"; havana_transcript \"OTTHUMT00000362751.1\";\n\
            chr1\tHAVANA\texon\t12613\t12721\t.\t+\t.\tgene_id \"ENSG00000223972.5\"; transcript_id \"ENST00000456328.2\"; gene_type \"transcribed_unprocessed_pseudogene\"; gene_name \"DDX11L1\"; transcript_type \"processed_transcript\"; transcript_name \"DDX11L1-202\"; exon_number 2; exon_id \"ENSE00003582793.1\"; level 2; transcript_support_level \"1\"; hgnc_id \"HGNC:37102\"; tag \"basic\"; havana_gene \"OTTHUMG00000000961.2\"; havana_transcript \"OTTHUMT00000362751.1\";\n\
            chr1\tHAVANA\texon\t13221\t14409\t.\t+\t.\tgene_id \"ENSG00000223972.5\"; transcript_id \"ENST00000456328.2\"; gene_type \"transcribed_unprocessed_pseudogene\"; gene_name \"DDX11L1\"; transcript_type \"processed_transcript\"; transcript_name \"DDX11L1-202\"; exon_number 3; exon_id \"ENSE00002312635.1\"; level 2; transcript_support_level \"1\"; hgnc_id \"HGNC:37102\"; tag \"basic\"; havana_gene \"OTTHUMG00000000961.2\"; havana_transcript \"OTTHUMT00000362751.1\";";

        let expected = Transcript {
            transcript_name: Some("DDX11L1-202".to_string()),
            transcript_id: "ENST00000456328.2".to_string(),
            gene_name: "DDX11L1".to_string(),
            gene_id: "ENSG00000223972.5".to_string(),
            is_coding: Some(false),
            chrom: "chr1".to_string(),
            left: Position::try_from(11869).unwrap(),
            right: Position::try_from(14409).unwrap(),
            strand: Strand::Forward,
        };
        assert_eq!(
            read_transcripts_from_gff(gff.as_bytes(), &Default::default()).unwrap()[0],
            expected
        );
        assert_eq!(
            read_transcripts_from_gtf(gtf.as_bytes(), &Default::default()).unwrap()[0],
            expected
        );
    }
}