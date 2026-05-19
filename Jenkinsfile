pipeline {
    agent any

    environment {
        HEADLESS       = 'true'
        LOGIN_ID       = credentials('E2E_LOGIN_ID')
        LOGIN_PW       = credentials('E2E_LOGIN_PW')
        PYTHONIOENCODING = 'utf-8'
        PYTHONUTF8     = '1'
    }

    stages {
        stage('Install dependencies') {
            steps {
                dir('e2e_den') {
                    bat 'C:\\Python38\\python.exe -m pip install -r requirements.txt'
                }
            }
        }

        stage('Run E2E tests') {
            steps {
                dir('e2e_den') {
                    bat 'if not exist reports mkdir reports'
                    bat 'C:\\Python38\\python.exe -m pytest --browser=chrome'
                    bat 'dir reports'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'e2e_den/reports/**/*', allowEmptyArchive: true
        }
    }
}
