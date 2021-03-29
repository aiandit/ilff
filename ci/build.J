pipeline {
    agent {
        label "python-builder"
    }

    stages {
        stage('Checkout') {
            steps {
                sh 'ls -l'
            }
        }
        stage('Build') {
            environment {
                PYTHON = 'python3'
            }
            steps {
                sh 'make allclean'
                sh 'make'
            }
        }
        stage('Test') {
            environment {
                PYTHON = 'python3'
            }
            steps {
                sh 'make check'
            }
        }
        stage('Deploy') {
            steps {
                archiveArtifacts artifacts: 'dist/*.tar.gz'
                archiveArtifacts artifacts: 'dist/*.whl'
                sh '''
scp dist/*.tar.gz dist/*.whl jenkins@fnc-jenkins:/mnt/software/builds/Python/ilff
'''
            }
        }
    }
}
