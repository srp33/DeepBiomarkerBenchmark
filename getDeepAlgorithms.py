import glob

algos = glob.glob("AlgorithmScripts/Classification/tsv/keras/*/*")
# algos_remove = glob.glob("AlgorithmScripts/Classification/tsv/mlr/multinom/*")

# for a in algos_remove:
#   algos.remove(a)

output_file = 'AllClassificationAlgorithms.list'
out = open(output_file, 'w')
for a in algos:
    out.write(a + '\n')
out.close()

algos_def = glob.glob("AlgorithmScripts/Classification/tsv/keras/resnet/default*")
# algos_remove = glob.glob("AlgorithmScripts/Classification/tsv/keras/resnet/default*")
#
# for a in algos_remove:
#     algos_def.remove(a)

output_file = 'AllClassificationAlgorithmsDefault.list'
out = open(output_file, 'w')
for a in algos_def:
    out.write(a + '\n')
out.close()
