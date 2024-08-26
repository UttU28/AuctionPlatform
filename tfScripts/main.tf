terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }
  backend "azurerm" {
    resource_group_name  = "thisstoragerg"
    storage_account_name = "dicestorage02"
    container_name       = "13form"
    key                  = "auctionState"
  }
}

data "azurerm_container_app_environment" "app_environment" {
  name                = local.dicesaralapply-app-environment
  resource_group_name = local.dicesaralapply-rg
}

resource "azurerm_container_app" "dicesaralapply" {
  name                         = "auctionplatform"
  container_app_environment_id = data.azurerm_container_app_environment.app_environment.id
  resource_group_name          = local.dicesaralapply-rg
  revision_mode                = "Single"

  template {
    container {
      name   = "${local.acrName}-random-string"
      image  = local.acrUrl
      cpu    = 0.75
      memory = "1.5Gi"
    }
  }

  secret {
    name  = "registry-credentials"
    value = local.acrPassword
  }

  registry {
    server               = "${local.acrName}.azurecr.io"
    username             = local.acrName
    password_secret_name = "registry-credentials"
  }

  provisioner "local-exec" {
    command = <<EOT
      sleep 20
      az containerapp ingress enable \
        --name auctionplatform \
        --resource-group ${local.dicesaralapply-rg} \
        --type external \
        --target-port 50505 \
        --transport auto \
        --allow-insecure false
    EOT
  }
}