import glob
import gzip
from sys import argv
import os
import re

results_dir = argv[1]
out_dir = 'Merged_Results'
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
out_dir = os.path.join(out_dir, results_dir)
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

metrics = os.path.join(out_dir, 'Metrics.tsv.gz')
auroc = os.path.join(out_dir, 'Metrics_AUROC.tsv.gz')
metric_files = glob.glob('{}/*/*/iteration*/*/Metrics.tsv'.format(results_dir))
header = 'DatasetID\tClass\tIteration\tClassifAlgoGroup\tMetric\tValue\tClassificationAlgorithm\n'
with gzip.open(metrics, 'wb') as fp:
    with gzip.open(auroc, 'wb') as fp2:
        fp.write(header.encode())
        fp2.write(header.encode())
        for file in metric_files:
            with open(file) as content:
                content.readline()
                for line in content:
                    data = line.rstrip('\n').split('\t')
                    classifier = data[0].split('___')
                    dataset_id = classifier[0]
                    label = classifier[1]
                    iteration = classifier[2].replace('iteration', '')
                    classif_algo_group = 'keras/{}'.format(data[2].split('/')[4])
                    params = re.sub(r'^[^_]*__[^_]*__[^_]*__', '', file.split('/')[-2])
                    classification_algorithm = '{}/{}'.format(classif_algo_group, params)
                    metric = data[3]
                    value = data[4]
                    fp.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(dataset_id, label, iteration, classif_algo_group,
                                                               metric, value, classification_algorithm).encode())
                    if metric == 'AUROC':
                        fp2.write(
                            '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(dataset_id, label, iteration, classif_algo_group,
                                                              metric, value, classification_algorithm).encode())

nested_metrics = os.path.join(out_dir, 'Nested_Metrics.tsv.gz')
nested_auroc = os.path.join(out_dir, 'Nested_Metrics_AUROC.tsv.gz')
nested_metric_files = glob.glob('{}/*/*/iteration*/*/Nested_Metrics.tsv'.format(results_dir))
nested_header = 'DatasetID\tClass\tOuterIteration\tInnerIteration\tClassificationAlgorithm\tMetric\tValue\n'
with gzip.open(nested_metrics, 'wb') as fp:
    with gzip.open(nested_auroc, 'wb') as fp2:
        fp.write(nested_header.encode())
        fp2.write(nested_header.encode())
        for file in nested_metric_files:
            with open(file) as content:
                content.readline()
                for line in content:
                    data = line.rstrip('\n').split('\t')
                    classifier = data[0].split('___')
                    dataset_id = classifier[0]
                    label = classifier[1]
                    outer_iteration = classifier[2].replace('iteration', '')
                    inner_iteration = data[2]
                    params = re.sub(r'^[^_]*__[^_]*__[^_]*__', '', file.split('/')[-2])
                    classification_algorithm = 'keras/{}/{}'.format(data[3].split('/')[4], params)
                    metric = data[4]
                    value = data[5]
                    fp.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(dataset_id, label, outer_iteration, inner_iteration,
                                                                   classification_algorithm, metric, value).encode())
                    if metric == 'AUROC':
                        fp2.write(
                            '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(dataset_id, label, outer_iteration, inner_iteration,
                                                                  classification_algorithm, metric, value).encode())

auroc_best = os.path.join(out_dir, 'Metrics_AUROC_Best.tsv.gz')
os.system('Rscript --vanilla SelectBestInnerResults_Classification.R {} {} {}'.format(nested_auroc, auroc, auroc_best))
