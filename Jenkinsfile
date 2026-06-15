pipeline {
    agent any

    environment {
        IMAGE_NAME = "bliss009/bliss_docker:latest"
        CONTAINER_NAME = "ai-model-api"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: 'https://github.com/ilovejwoo1004-bit/ai-model-cicd-practice.git'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-token',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Docker Push') {
            steps {
                sh 'docker push $IMAGE_NAME'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker rm -f $CONTAINER_NAME || true
                docker pull $IMAGE_NAME
                docker compose down || true
                docker compose pull
                docker compose up -d
                '''
            }
        }

        stage('Test API') {
            steps {
                sh '''
                sleep 5
                curl http://localhost:8000/
                curl "http://localhost:8000/predict?value=1.5"
                '''
            }
        }
    }
}




Dashboard
→ New Item
→ ai-model-cicd 입력
→ Pipeline 선택
→ OK



Pipeline
→ Definition: Pipeline script from SCM
→ SCM: Git
→ Repository URL: https://github.com/bliss009/ai-model-cicd-practice.git
→ Credentials: github-token
→ Branch Specifier: */main
→ Script Path: Jenkinsfile
→ Save






