import jenkins.model.*
import org.allurereport.jenkins.AllureReportPublisher
import org.jenkinsci.plugins.allure.AllureGlobalTool

def instance = Jenkins.getInstanceOrNull()
if (instance == null) {
    println "Jenkins instance is null"
    return
}

// Register Allure CLI as a global tool
def descriptor = instance.getDescriptorByType(AllureGlobalTool.DescriptorImpl.class)
if (descriptor != null) {
    def installations = descriptor.getInstallations()
    def existing = installations.find { it.name == 'Allure' }
    if (existing == null) {
        def allureInstallation = new AllureGlobalTool(
            'Allure',           // name
            '/opt/allure',      // home
            null                // properties (optional)
        )
        descriptor.setInstallations(allureInstallation)
        descriptor.save()
        println "Allure global tool 'Allure' registered at /opt/allure"
    } else {
        println "Allure global tool 'Allure' already exists"
    }
} else {
    println "AllureGlobalTool descriptor not found"
}

instance.save()