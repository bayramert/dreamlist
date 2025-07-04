pipeline {
    agent any

    environment {
        // Docker Hub kullanıcı adınız
        DOCKER_USERNAME = 'bayramert'
        // Jenkins'te tanımladığınız Docker Hub kimlik bilgisi ID'si. Ekran görüntünüze göre DOĞRU OLAN BUDUR.
        DOCKER_PASS = credentials('dockerhub-credentials') 

        // Jenkins'te tanımladığınız K3s SSH kimlik bilgisi ID'si. Ekran görüntünüze göre DOĞRU OLAN BUDUR.
        K3S_SSH_CREDENTIAL_ID = 'k3s-ssh-credentials'

        // K3s Master sunucunuzun IP adresi
        K3S_MASTER_IP = '10.77.3.19'
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
                // GitHub deponuz public olduğu için 'credentialsId: 'github-token'' kısmını kaldırdık.
                // Bu, "CredentialId 'github-token' could not be found." uyarısını giderecektir.
                git url: 'https://github.com/bayramert/dreamlist.git', branch: 'main' 
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Docker imajı oluşturuluyor: ${DOCKER_USERNAME}/dreamlist-app:latest"
                    sh "docker build -t ${DOCKER_USERNAME}/dreamlist-app:latest ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // DOCKER_PASS değişkeni environment bloğunda credentials('dockerhub-credentials') olarak ayarlandığı için
                    // withCredentials burada doğru ID'yi kullanacaktır.
                    withCredentials([usernamePassword(credentialsId: DOCKER_PASS, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME_VAR')]) {
                        echo "Docker Hub'a giriş yapılıyor..."
                        sh "echo ${DOCKER_PASSWORD} | docker login --username ${DOCKER_USERNAME_VAR} --password-stdin"

                        echo "Docker imajı push ediliyor..."
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
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-dreamlist-app.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-dreamlist-app.yaml"

                        echo "Kubernetes kaynakları uygulanıyor..."
                        // K3s master üzerindeki izin sorununu çözmek için kubectl komutlarının başında 'sudo ' ekledik.
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