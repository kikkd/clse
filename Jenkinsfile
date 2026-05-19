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
    }
}
