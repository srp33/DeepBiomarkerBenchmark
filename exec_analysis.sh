#!/bin/bash

analysis=$1
classifications=$2
currentDir=$(pwd)
tmpDir=/tmp/${analysis}_parse

###########################################
# Preparatory steps
###########################################

currentDir=$(pwd)
rm -rf AlgorithmScripts
cd /tmp
rm -rf ShinyLearner
git clone https://github.com/srp33/ShinyLearner.git
mv ShinyLearner/AlgorithmScripts $currentDir
rm -rf ShinyLearner
cd $currentDir
#python3 getDeepAlgorithms.py

###########################################
# Executing commands
###########################################

dockerCommandsFile=${analysis}_Docker_Commands.sh
summaryFile=${analysis}_Summary.tsv

if [[ ${analysis} == 'Analysis3' ]]
then stopIteration=50; algorithms=AllClassificationAlgorithmsDefault.list;
else stopIteration=5; algorithms=AllClassificationAlgorithms.list;
fi

startIteration=1
delay=1

numJobs=10
memoryGigs=100
swapMemoryGigs=100
hoursMax=72
numCores=1
shinyLearnerVersion=474

rm -f $dockerCommandsFile
python3 create_docker_commands.py ${analysis} $startIteration $stopIteration $memoryGigs $swapMemoryGigs $hoursMax $numCores $algorithms $classifications Predictions.tsv $dockerCommandsFile $summaryFile $shinyLearnerVersion $(hostname)
#vim $dockerCommandsFile
#exit 0

jobLogFile=${analysis}.job.log
rm -f $jobLogFile
parallel --retries 0 --shuf --progress --eta --delay $delay --joblog $jobLogFile -j $numJobs -- < $dockerCommandsFile
echo Done executing!!!!!!!!!!!!!!!!!!!!!!!!
