# workflow/scripts/deseq2_analysis.R
#!/usr/bin/env Rscript


library(DESeq2)
library(tidyverse)
library(optparse)

# 解析命令行参数
option_list <- list(
  make_option(c("-c", "--counts"), type="character", default=NULL,
              help="gene count path", metavar="character"),
  make_option(c("-m", "--metadata"), type="character", default=NULL,
              help="metadata path", metavar="character"),
  make_option(c("-o", "--output"), type="character", default="./output",
              help="output path", metavar="character"),
  make_option(c("-p", "--pvalue"), type="double", default=0.05,
              help="P value", metavar="double"),
  make_option(c("-f", "--log2fc"), type="double", default=1.0,
              help="log2FC", metavar="double")
)

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)

# 创建输出目录
if (!dir.exists(opt$output)) {
  dir.create(opt$output, recursive=TRUE)
}

cat("Reading data\n")
counts <- read.csv(opt$counts, row.names=1)
metadata <- read.csv(opt$metadata)

cat("Starting analysis\n")

# 构建DESeq2对象
dds <- DESeqDataSetFromMatrix(
  countData = round(counts),
  colData = metadata,
  design = ~ group
)
metadata$group <- factor(metadata$group, levels=unique(metadata$group))

# 执行DESeq2
dds <- DESeq(dds)

# 提取结果
res <- results(dds, contrast=c("group", 
                               levels(metadata$group)[2], 
                               levels(metadata$group)[1]))

# 排序并添加基因名
res_df <- as.data.frame(res)
res_df$gene <- rownames(res_df)

# 添加显著性标记
res_df$significant <- ifelse(res_df$padj < opt$pvalue & 
                             abs(res_df$log2FoldChange) > opt$log2fc,
                             TRUE, FALSE)

# 保存完整结果
write.csv(res_df, file.path(opt$output, "deseq2_results.csv"), row.names=FALSE)

# 保存显著基因
sig_genes <- res_df[which(res_df$significant==TRUE), ]
write.csv(sig_genes, file.path(opt$output, "significant_genes.csv"), row.names=FALSE)

# 统计信息
n_up <- sum(sig_genes$log2FoldChange > 0, na.rm=TRUE)
n_down <- sum(sig_genes$log2FoldChange < 0, na.rm=TRUE)

cat("\n DESeq2! Analysis done!\n")
cat(sprintf("  All genes: %d\n", nrow(res_df)))
cat(sprintf("  Up-regulated: %d\n", n_up))
cat(sprintf("  Down-regulated: %d\n", n_down))
cat(sprintf("  DEG: %d\n", n_up + n_down))

# 保存统计信息
stats <- list(
  group1 = levels(metadata$group)[1],
  group2 = levels(metadata$group)[2],
  total_genes = nrow(res_df),
  up_regulated = n_up,
  down_regulated = n_down,
  significant_total = n_up + n_down,
  pvalue_threshold = opt$pvalue,
  log2fc_threshold = opt$log2fc
)

jsonlite::write_json(stats, file.path(opt$output, "statistics.json"),auto_unbox = TRUE)

# 生成火山图
if (nrow(res_df) > 0) {
  library(ggplot2)
  
  p <- ggplot(res_df, aes(x=log2FoldChange, y=-log10(padj))) +
    geom_point(aes(color=significant), alpha=0.6, size=1) +
    scale_color_manual(values=c("FALSE"="gray", "TRUE"="red")) +
    geom_hline(yintercept=-log10(opt$pvalue), linetype="dashed", color="blue") +
    geom_vline(xintercept=c(-opt$log2fc, opt$log2fc), linetype="dashed", color="blue") +
    theme_minimal() +
    labs(title="Volcano Plot",
         x="log2 Fold Change",
         y="-log10(adjusted p-value)")
  
  ggsave(file.path(opt$output, "volcano.png"), p, width=10, height=8)
  cat("Volcano plot done!\n")
}

cat("Results saved in:", opt$output, "\n")

