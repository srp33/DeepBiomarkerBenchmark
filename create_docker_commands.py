import glob
import os
import shutil
import sys

analysis = sys.argv[1]
startIteration = int(sys.argv[2])
stopIteration = int(sys.argv[3])
memoryGigs = sys.argv[4]
swapMemoryGigs = sys.argv[5]
hoursMax = sys.argv[6]
numCores = sys.argv[7]
algorithmsFilePath = sys.argv[8]
classificationsFilePath = sys.argv[9]
outFileToCheck = sys.argv[10]
dockerOutFilePath = sys.argv[11]
summaryOutFilePath = sys.argv[12]
shinyLearnerVersion = sys.argv[13]
host = sys.argv[14]

with open(algorithmsFilePath, 'r') as f:
    allAlgorithms = f.read().splitlines()
allAlgorithms = set([x.replace('AlgorithmScripts/Classification/', '') for x in allAlgorithms if not x.startswith("#")])

with open(classificationsFilePath, 'r') as g:
    allClassifications = [x for x in g.read().splitlines() if not x.startswith("#")]

if host == 'bosai':
    docker_version = 'nvidia-docker'
    docker_image = 'srp33/shinylearner_gpu'
else:
    docker_version = 'docker'
    docker_image = 'srp33/shinylearner'

if analysis != 'Analysis1' and analysis != 'Analysis2':
    covariates = True
else:
    covariates = False

if analysis == 'Analysis4':
    shiny_algo = 'nestedclassification_montecarlo'
    iterations = '--outer-iterations 1 --inner-iterations 5'
else:
    shiny_algo = 'classification_montecarlo'
    iterations = '--iterations 1'
    # allAlgorithms = [x.split("__")[0] for x in allAlgorithms]
    # allAlgorithms = set(allAlgorithms)

currentWorkingDir = os.path.dirname(os.path.realpath(__file__))

dockerCommandFilePaths = []
summaryLines = []

if os.path.exists(analysis + '_Commands/'):
    shutil.rmtree(analysis + '_Commands/')

for c in allClassifications:
    gseVar = c.split('\t')[0]
    classVar = c.split('\t')[1]
    covVar = c.split('\t')[2]

    input_data = list()
    dataset_path = 'Biomarker_Benchmark_Data/' + gseVar + '/'
    expression_path = dataset_path + gseVar + '.txt.gz'
    class_path = dataset_path + 'Class/' + classVar + '.txt'

    if covariates and covVar != 'no_covariates':
        input_data = covVar.split(',')
        input_data = [dataset_path + 'Covariate/' + i + '.txt' for i in input_data]

    input_data.append(expression_path)
    input_data.append(class_path)

    for i in range(startIteration, 1 + stopIteration):
        print(analysis + ' ' + gseVar + ' ' + classVar + ' ' + 'iteration' + str(i))
        path = analysis + '/' + gseVar + '/' + classVar + '/iteration' + str(i) + '/*/' + outFileToCheck
        # print(path)
        # exit(0)

        executed_algos = glob.glob(path)
        executed_algos = [x.split('/')[4].replace('__', '/', 3) for x in executed_algos]
        executed_algos = set(executed_algos)

        not_executed_algos = allAlgorithms - executed_algos

        summaryLines.append([gseVar, classVar, covVar, i, len(executed_algos), len(not_executed_algos)])

        if len(not_executed_algos) > 0:
            for algo in not_executed_algos:
                algoName = algo.replace('/', '__')

                data_all = ''
                for d in input_data:
                    data_all = '{}--data "/InputData/{}" '.format(data_all, d)

                outDir = '/Analysis/DeepBiomarkerBenchmark/{analysis}/{gseVar}/{classVar}/iteration{i}/{algoName}/' \
                    .format(analysis=analysis, gseVar=gseVar, classVar=classVar, i=i, algoName=algoName)

                out = 'if [ ! -f {outDir}{outFileToCheck} ]\nthen\n  {docker_version} run ' \
                      '--memory {memoryGigs}G ' \
                      '--memory-swap {swapMemoryGigs}G ' \
                      '--rm ' \
                      '-i ' \
                      '-v "/Analysis/BiomarkerBenchmark/":/InputData ' \
                      '-v "{outDir}":/OutputData {docker_image}:version{shinyLearnerVersion} ' \
                      'timeout -s 9 {hoursMax}h "/UserScripts/{shiny_algo}" {data_all}' \
                      '--description {gseVar}___{classVar}___iteration{i} ' \
                      '{iterations} ' \
                      '--classif-algo "AlgorithmScripts/Classification/{algo}" ' \
                      '--output-dir "/OutputData" ' \
                      '--scale robust ' \
                      '--seed {i} ' \
                      '--verbose false ' \
                      '--num-cores {numCores}' \
                      '\nfi'.format(outDir=outDir, outFileToCheck=outFileToCheck, memoryGigs=memoryGigs,
                                    swapMemoryGigs=swapMemoryGigs, shinyLearnerVersion=shinyLearnerVersion,
                                    hoursMax=hoursMax, data_all=data_all, gseVar=gseVar, classVar=classVar, i=i,
                                    algo=algo, numCores=numCores, docker_version=docker_version,
                                    docker_image=docker_image, shiny_algo=shiny_algo, iterations=iterations)

                commandFilePath = '{}_Commands/{}/{}/iteration{}/{}.sh'.format(analysis, gseVar, classVar, i, algoName)
                if not os.path.exists(os.path.dirname(commandFilePath)):
                    os.makedirs(os.path.dirname(commandFilePath))

                with open(commandFilePath, 'w') as outFile:
                    outFile.write(out + '\n')

                dockerCommandFilePaths.append(commandFilePath)

with open(summaryOutFilePath, 'w') as summaryOutFile:
    summaryOutFile.write("DataSet\tClass\tCovariates\tIteration\tNumComplete\tNumPending\n")
    for line in summaryLines:
        summaryOutFile.write("\t".join([str(x) for x in line]) + "\n")

if len(dockerCommandFilePaths) == 0:
    print('All commands have been executed!')
else:
    with open(dockerOutFilePath, 'w') as dockerOutFile:
        for command in dockerCommandFilePaths:
            dockerOutFile.write("bash {}\n".format(command))
