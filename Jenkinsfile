// Jenkinsfile
pipeline {
    agent any // Boru hattının herhangi bir Jenkins aracısında çalışacağını belirtir

    environment {
        // Ortam değişkenleri, boru hattı boyunca kullanılacak değerleri tanımlar.
        DOCKER_HUB_USERNAME = 'bayramert' // Kendi Docker Hub kullanıcı adınız
        DOCKER_HUB_CREDENTIALS_ID = 'dockerhub-credentials' // Jenkins'teki Docker Hub kimlik bilgilerinin ID'si
        KUBERNETES_CREDENTIALS_ID = 'k3s-ssh-credentials' // Jenkins'teki K3s SSH kimlik bilgilerinin ID'si
        K3S_NODE_IP = '10.77.3.19' // K3s master sunucunuzun IP adresi
        K3S_NODE_USER = 'ubuntu' // K3s master SSH kullanıcı adınız
        GITHUB_CREDENTIALS_ID = 'github-token' // Jenkins'teki GitHub Personal Access Token'ınızın ID'si
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "Kod GitHub reposundan çekiliyor..."
                // GitHub token'ını (Secret text türünde) kullanarak depoyu klonla
                // Bu adım, Jenkins'in SCM UI'ından Credentials seçeneği görünmese bile çalışacaktır.
                git branch: 'main', credentialsId: "${GITHUB_CREDENTIALS_ID}", url: 'https://github.com/bayramert/dreamlist.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Docker imajını oluşturur.
                    // '.': Dockerfile'ın mevcut dizinde olduğunu belirtir.
                    echo "Docker imajı oluşturuluyor: ${DOCKER_HUB_USERNAME}/dreamlist-app:latest"
                    sh "docker build -t ${DOCKER_HUB_USERNAME}/dreamlist-app:latest ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Docker Hub'a giriş yapar ve imajı gönderir.
                    // 'withCredentials' Jenkins'te tanımlı kimlik bilgilerini güvenli bir şekilde kullanmayı sağlar.
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        echo "Docker Hub'a giriş yapılıyor..."
                        sh "echo \$DOCKER_PASS | docker login --username \$DOCKER_USER --password-stdin"
                        echo "Docker imajı push ediliyor..."
                        sh "docker push ${DOCKER_HUB_USERNAME}/dreamlist-app:latest"
                        echo "Docker Hub'dan çıkış yapılıyor..."
                        sh "docker logout"
                    }
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                script {
                    // Uygulama dosyalarını (secret, mongodb, dreamlist-app YAML'ler) K3s master'a kopyalar ve dağıtım yapar.
                    // 'withCredentials' Jenkins'te tanımlı SSH anahtarını güvenli bir şekilde kullanmayı sağlar.
                    withCredentials([sshUserPrivateKey(credentialsId: "${KUBERNETES_CREDENTIALS_ID}", keyFileVariable: 'SSH_KEY_FILE')]) {
                        echo "SSH anahtar dosyası izinleri ayarlanıyor..."
                        sh '''
                            chmod 600 $SSH_KEY_FILE

                            echo "Kubernetes YAML dosyaları K3s master'a kopyalanıyor..."
                            scp -i $SSH_KEY_FILE -o StrictHostKeyChecking=no k3s-secret.yaml ${K3S_NODE_USER}@${K3S_NODE_IP}:/tmp/k3s-secret.yaml
                            scp -i $SSH_KEY_FILE -o StrictHostKeyChecking=no k3s-mongodb.yaml ${K3S_NODE_USER}@${K3S_NODE_IP}:/tmp/k3s-mongodb.yaml
                            scp -i $SSH_KEY_FILE -o StrictHostKeyChecking=no k3s-dreamlist-app.yaml ${K3S_NODE_USER}@${K3S_NODE_IP}:/tmp/k3s-dreamlist-app.yaml

                            echo "Kubernetes kaynakları uygulanıyor..."
                            ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no ${K3S_NODE_USER}@${K3S_NODE_IP} "kubectl apply -f /tmp/k3s-secret.yaml"
                            ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no ${K3S_NODE_USER}@${K3S_NODE_IP} "kubectl apply -f /tmp/k3s-mongodb.yaml"
                            ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no ${K3S_NODE_USER}@${K3S_NODE_IP} "kubectl apply -f /tmp/k3s-dreamlist-app.yaml"

                            echo "Kopyalanan geçici YAML dosyaları K3s master'dan siliniyor..."
                            ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no ${K3S_NODE_USER}@${K3S_NODE_IP} "rm /tmp/k3s-secret.yaml /tmp/k3s-mongodb.yaml /tmp/k3s-dreamlist-app.yaml"
                        '''
                    }
                }
            }
        }
    }
    post {
        always {
            // Her derleme sonunda çalışacak adımlar (örn: bildirimler, temizlik)
            echo "Boru hattı tamamlandı."
        }
        failure {
            // Boru hattı başarısız olursa çalışacak adımlar
            echo "Boru hattı başarısız oldu!"
            // Örneğin, bir bildirim gönderebilirsiniz.
        }
        success {
            // Boru hattı başarılı olursa çalışacak adımlar
            echo "Boru hattı başarıyla tamamlandı!"
        }
    }
}