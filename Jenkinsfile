pipeline {
    agent any

    environment {
        PYTHONDONTWRITEBYTECODE = '1'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from Git repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt pytest
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated test suite with pytest...'
                sh '''
                    . .venv/bin/activate
                    pytest -v
                '''
            }
        }

        // =========================================================================
        // PLACEHOLDER STAGES FOR FUTURE PHASES
        // =========================================================================

        /*
        stage('Security Scan (Trivy)') {
            steps {
                // Placeholder: Scan repository and container image for vulnerabilities
                echo 'Trivy security scanning stage will be implemented in a later phase.'
                // sh 'trivy fs --severity HIGH,CRITICAL .'
            }
        }

        stage('Docker Build') {
            steps {
                // Placeholder: Build production container image
                echo 'Docker build stage will be implemented in a later phase.'
                // sh 'docker build -t parking-reservation-app:${BUILD_NUMBER} .'
            }
        }

        stage('Docker Push') {
            steps {
                // Placeholder: Push Docker image to registry (e.g., Docker Hub)
                echo 'Docker push stage will be implemented in a later phase.'
                // withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                //     sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                //     sh 'docker push <username>/parking-reservation-app:${BUILD_NUMBER}'
                // }
            }
        }
        */
    }

    post {
        always {
            echo 'Pipeline run finished.'
        }
        success {
            echo 'Build and tests succeeded!'
        }
        failure {
            echo 'Pipeline failed. Check stage logs for details.'
        }
    }
}
