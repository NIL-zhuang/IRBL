pipeline {
    agent any
    triggers {
       GenericTrigger(
           causeString: 'Triggered by develop',
           genericVariables: [[key: 'ref', value: '$.ref']],
           printContributedVariables: true,
           printPostContent: true,
           regexpFilterExpression: 'refs/heads/' + BRANCH_NAME,
           regexpFilterText: '$ref',
           token: 'siegelion'
       )
    }
    stages {
       stage('build') {
          steps {
             echo 'Notify GitLab'
             sh "/usr/lib/maven/apache-maven-3.6.3/bin/mvn install"
             updateGitlabCommitStatus name: 'build', state: 'pending'
             updateGitlabCommitStatus name: 'test', state: 'success'
          }
       }
       stage('test') {
           steps {
               updateGitlabCommitStatus name: 'test', state: 'pending'
               echo 'start python test'
               sh "/lib/miniconda/envs/py37/bin/python src/main/python/irbl/test.py"
               echo 'start java test'
               sh "/usr/lib/maven/apache-maven-3.6.3/bin/mvn org.jacoco:jacoco-maven-plugin:prepare-agent -f pom.xml clean test -Dautoconfig.skip=true -Dmaven.test.skip=false -Dmaven.test.failure.ignore=true"
               jacoco changeBuildStatus: true, maximumLineCoverage: '10'
           }
       }
       stage('master deploy test'){
          when{
             branch 'master'
          }
          steps{
             echo 'springboot'
             sh "/usr/lib/maven/apache-maven-3.6.3/bin/mvn spring-boot:run"
             // sh "mvn spring-boot:run"
             updateGitlabCommitStatus name: 'test', state: 'success'
          }
       }
       stage('dev deploy test'){
          when{
             branch 'dev'
          }
          steps{
             echo 'springboot'
             sh "/usr/lib/maven/apache-maven-3.6.3/bin/mvn spring-boot:run"
             // sh "mvn spring-boot:run"
             updateGitlabCommitStatus name: 'test', state: 'success'
          }
       }
    }
 }
