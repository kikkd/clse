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
                    bat 'C:\\Python38\\python.exe -m pip install flake8 flake8-html --quiet'
                    bat 'if not exist reports\\lint mkdir reports\\lint'
                    bat 'C:\\Python38\\python.exe -m flake8 --format=html --htmldir=reports/lint . || exit 0'
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'e2e_den/reports/lint',
                reportFiles: 'index.html',
                reportName: 'Lint Report'
            ])
            slackSend channel: '#automation-test',
                      color: 'warning',
                      message: "🔍 Lint 결과: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n상세 보기: ${env.BUILD_URL}Lint_20Report"
        }
    }
}
