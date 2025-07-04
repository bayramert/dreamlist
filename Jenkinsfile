pipeline {
    agent any

    environment {
        DOCKER_USERNAME = 'bayramert'
        K3S_SSH_CREDENTIAL_ID = 'k3s-ssh-credentials'
        K3S_MASTER_IP = '10.77.3.19'
        // Yeni ortam değişkeni: Build numarası ile imaj etiketi
        IMAGE_TAG = "${DOCKER_USERNAME}/dreamlist-app:${BUILD_NUMBER}"
    }

    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Code') {
            steps {
                echo 'Kod GitHub reposundan çekiliyor...'
                git url: 'https://github.com/bayramert/dreamlist.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Docker imajı oluşturuluyor: ${IMAGE_TAG}" // :latest yerine yeni tag
                    sh "docker build -t ${IMAGE_TAG} ."
                    // Ayrıca eski :latest etiketini de ekleyebilirsiniz, bu opsiyoneldir.
                    sh "docker tag ${IMAGE_TAG} ${DOCKER_USERNAME}/dreamlist-app:latest"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME_VAR')]) {
                        echo "Docker Hub'a giriş yapılıyor..."
                        sh "echo ${DOCKER_PASSWORD} | docker login --username ${DOCKER_USERNAME_VAR} --password-stdin"

                        echo "Docker imajı push ediliyor: ${IMAGE_TAG}" // Yeni tag push ediliyor
                        sh "docker push ${IMAGE_TAG}"
                        echo "Docker imajı push ediliyor: ${DOCKER_USERNAME}/dreamlist-app:latest" // :latest de push ediliyor
                        sh "docker push ${DOCKER_USERNAME}/dreamlist-app:latest"


                        echo "Docker Hub'dan çıkış yapılıyor..."
                        sh "docker logout"
                    }
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: K3S_SSH_CREDENTIAL_ID, keyFileVariable: 'SSH_KEY_FILE')]) {
                        echo "SSH anahtar dosyası izinleri ayarlanıyor..."
                        sh "chmod 600 ${SSH_KEY_FILE}"

                        echo "Kubernetes YAML dosyaları K3s master'a kopyalanıyor..."
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-secret.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-secret.yaml"
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-mongodb.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-mongodb.yaml"

                        // k3s-dreamlist-app.yaml'ı dinamik olarak güncellemek için yeni bir adım ekleyeceğiz
                        echo "k3s-dreamlist-app.yaml dosyası güncelleniyor ve kopyalanıyor..."
                        sh "sed \"s|image: ${DOCKER_USERNAME}/dreamlist-app:latest|image: ${IMAGE_TAG}|g\" k3s-dreamlist-app.yaml > k3s-dreamlist-app-updated.yaml"
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-dreamlist-app-updated.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-dreamlist-app.yaml"


                        echo "Kubernetes kaynakları uygulanıyor..."
                        sh "ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no ubuntu@${K3S_MASTER_IP} 'sudo kubectl apply -f /tmp/k3s-secret.yaml'"
                        sh "ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no ubuntu@${K3S_MASTER_IP} 'sudo kubectl apply -f /tmp/k3s-mongodb.yaml'"
                        sh "ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no ubuntu@${K3S_MASTER_IP} 'sudo kubectl apply -f /tmp/k3s-dreamlist-app.yaml'"

                        echo "Geçici YAML dosyaları K3s master'dan siliniyor..."
                        sh "ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no ubuntu@${K3S_MASTER_IP} 'rm /tmp/k3s-secret.yaml /tmp/k3s-mongodb.yaml /tmp/k3s-dreamlist-app.yaml'"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Boru hattı tamamlandı."
        }
        success {
            echo "Boru hattı başarıyla tamamlandı!"
        }
        failure {
            echo "Boru hattı başarısız oldu!"
        }
    }
}