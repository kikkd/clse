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
            parallel {
                stage('Login Tests') {
                    steps {
                        dir('e2e_den') {
                            bat 'if not exist reports mkdir reports'
                            bat 'C:\\Python38\\python.exe -m pytest tests/test_login.py --browser=chrome --html=reports/report_login.html'
                        }
                    }
                }
                stage('Logged-in Tests') {
                    steps {
                        dir('e2e_den') {
                            bat 'if not exist reports mkdir reports'
                            bat 'C:\\Python38\\python.exe -m pytest tests/test_main.py   --browser=chrome --html=reports/report_main.html'
                            bat 'C:\\Python38\\python.exe -m pytest tests/test_search.py --browser=chrome --html=reports/report_search.html'
                            bat 'C:\\Python38\\python.exe -m pytest tests/test_map.py    --browser=chrome --html=reports/report_map.html'
                        }
                    }
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
                reportDir: 'e2e_den/reports',
                reportFiles: 'report_login.html,report_main.html,report_search.html,report_map.html',
                reportName: 'E2E Test Report'
            ])
            archiveArtifacts artifacts: 'e2e_den/reports/**', allowEmptyArchive: true
        }
        failure {
            mail to: 'ch01@osstem.com',
                 subject: "[Jenkins] 빌드 실패: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "E2E 테스트가 실패했습니다. 결과 report 참조 후 재 빌드 부탁드립니다.\n\n빌드 URL: ${env.BUILD_URL}"
            slackSend channel: '#general',
                      color: 'danger',
                      message: "❌ 빌드 실패: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n결과 report 참조 후 재 빌드 부탁드립니다.\n빌드 URL: ${env.BUILD_URL}"
        }
        success {
            mail to: 'ch01@osstem.com',
                 subject: "[Jenkins] 빌드 성공: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "E2E 테스트가 성공했습니다. 결과 report 참조 및 main 브랜치 머지 부탁드립니다. \n\n빌드 URL: ${env.BUILD_URL}"
            slackSend channel: '#general',
                      color: 'good',
                      message: "✅ 빌드 성공: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n결과 report 참조 및 main 브랜치 머지 부탁드립니다.\n빌드 URL: ${env.BUILD_URL}"
        }
    }
}
