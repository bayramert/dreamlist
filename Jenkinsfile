pipeline {
    agent any // Jenkins agent'ının herhangi bir uygun düğümde çalışmasını sağlar

    environment {
        // Docker Hub kullanıcı adınızı ve kimlik bilgisi ID'nizi buraya ekleyin
        DOCKER_USERNAME = 'bayramert'
        DOCKER_PASS = credentials('dockerhub-credentials') // Jenkins'te tanımladığınız Docker Hub kimlik bilgisi ID'si
        
        // K3s SSH Kimlik Bilgisi ID'si (Jenkins'te tanımlı)
        K3S_SSH_CREDENTIAL_ID = 'k3s-ssh-credentials' // Sizin k3s-ssh-credentials olarak kullandığınız ID
        
        // K3s Master IP Adresi
        K3S_MASTER_IP = '10.77.3.19' // K3s master sunucunuzun IP adresi
    }

    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                // Bu aşama genellikle Jenkins'in SCM Checkout özelliği tarafından otomatik olarak yönetilir.
                // Manuel bir 'git' komutuna ihtiyaç duyulmayabilir, ancak pipeline'ınızda varsa kalsın.
                checkout scm
            }
        }

        stage('Checkout Code') {
            steps {
                echo 'Kod GitHub reposundan çekiliyor...'
                // Kodunuzu tekrar çekmek için git komutu. İlk 'checkout scm' zaten çekmiş olabilir.
                // Eğer projeniz sadece Jenkinsfile içeriyorsa, bu aşama gereksiz olabilir.
                // credentialsId "github-token" uyarısı için: Eğer özel repo ise bu kimlik bilgisi gereklidir.
                // Public repo ise veya kimlik bilgisi gerekmiyorsa bu uyarıyı dikkate almayabilirsiniz.
                git url: 'https://github.com/bayramert/dreamlist.git', branch: 'main', credentialsId: 'github-token' // 'github-token' kimlik bilgisi ID'nizi ayarladığınızdan emin olun veya silin
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Docker imajı oluşturuluyor: ${DOCKER_USERNAME}/dreamlist-app:latest"
                    // Dockerfile'ın projenizin kök dizininde olduğunu varsayarız.
                    sh "docker build -t ${DOCKER_USERNAME}/dreamlist-app:latest ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
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
                        // YAML dosyalarınızın projenizin kök dizininde olduğunu varsayılır.
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-secret.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-secret.yaml"
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-mongodb.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-mongodb.yaml"
                        sh "scp -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=no k3s-dreamlist-app.yaml ubuntu@${K3S_MASTER_IP}:/tmp/k3s-dreamlist-app.yaml"

                        echo "Kubernetes kaynakları uygulanıyor..."
                        // BURADAKİ DEĞİŞİKLİK: kubectl komutlarının başına 'sudo ' eklendi.
                        // Uzak sunucuda çalıştırılan komutun tek tırnak ( '' ) içine alındığına DİKKAT EDİN.
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