pipeline {
    agent any

    environment {
        PYTHONIOENCODING = 'utf-8'
        PYTHONUTF8       = '1'
    }

    stages {
        stage('SBT - Lint') {
            steps {
                dir('e2e_den') {
                    bat 'C:\\Python38\\python.exe -m pip install flake8 --quiet'
                    bat 'if not exist reports mkdir reports'
                    bat 'C:\\Python38\\python.exe -m flake8 . > reports/lint_report.txt || exit 0'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'e2e_den/reports/lint_report.txt', allowEmptyArchive: true
            slackSend channel: '#automation-test',
                      color: 'warning',
                      message: "🔍 Lint 결과: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n상세 보기: ${env.BUILD_URL}artifact/e2e_den/reports/lint_report.txt"
        }
    }
}
