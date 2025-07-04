// Jenkinsfile
pipeline {
    agent any // Build'in herhangi bir uygun Jenkins agent'ında çalışmasını sağlar

    environment {
        // Docker Hub kullanıcı adınızı buraya yazın
        DOCKER_HUB_USERNAME = 'bayramert' 
        // Docker Hub kimlik bilgileriniz için Jenkins Credentials ID'sini buraya yazın
        DOCKER_HUB_CREDENTIALS_ID = 'dockerhub-credentials' 
        // K3s kümenize bağlanmak için gerekli SSH/kubeconfig bilgileri için Jenkins Credentials ID'si
        // Bu genellikle K3s master düğümüne SSH ile bağlanıp kubectl komutlarını çalıştırmak içindir.
        // Veya Jenkins agent'ınızda kubeconfig yapılandırıldıysa buna gerek kalmayabilir.
        KUBERNETES_CREDENTIALS_ID = 'k3s-ssh-credentials' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', credentialsId: 'github-token', url: 'https://github.com/bayramert/dreamlist-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Dockerfile'ın bulunduğu dizine git
                    dir('.') {
                        // Docker Hub'a giriş yapma
                        withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh "docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}"
                        }
                        // Docker imajını build et
                        sh "docker build -t ${DOCKER_HUB_USERNAME}/dreamlist-app:latest ."
                        // Docker imajını push et
                        sh "docker push ${DOCKER_HUB_USERNAME}/dreamlist-app:latest"
                    }
                }
            }
        }

        stage('Deploy to K3s') {
            steps {
                script {
                    // K3s bağlantısı için SSH kimlik bilgileriyle
                    withCredentials([sshUserPrivateKey(credentialsId: "${KUBERNETES_CREDENTIALS_ID}", keyFileVariable: 'SSH_KEY_FILE')]) {
                        sh '''
                            chmod 600 $SSH_KEY_FILE
                            # K3s düğümünüze SSH ile bağlanıp kubectl komutlarını çalıştırın
                            # Aşağıdaki komutları kendi K3s kurulumunuza göre ayarlayın.
                            # Eğer Jenkins agent'ınız K3s kümesinin bir parçasıysa veya kubeconfig'i yapılandırılmışsa, 
                            # SSH'a gerek kalmadan doğrudan kubectl komutlarını çalıştırabilirsiniz.
                            # Örnek: ssh -i $SSH_KEY_FILE user@your-k3s-node-ip "kubectl apply -f /path/to/your/k3s-mongodb.yaml"
                            # Örnek: ssh -i $SSH_KEY_FILE user@your-k3s-node-ip "kubectl apply -f /path/to/your/k3s-secret.yaml"
                            # Örnek: ssh -i $SSH_KEY_FILE user@your-k3s-node-ip "kubectl apply -f /path/to/your/k3s-dreamlist-app.yaml"

                            # Alternatif olarak, eğer kubectl Jenkins agent'ında kurulu ve yapılandırılmışsa:
                            kubectl apply -f k3s-secret.yaml
                            kubectl apply -f k3s-mongodb.yaml
                            kubectl apply -f k3s-dreamlist-app.yaml
                        '''
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs() // Workspace'i temizle
        }
        success {
            echo 'Pipeline başarıyla tamamlandı!'
        }
        failure {
            echo 'Pipeline başarısız oldu!'
        }
    }
}
