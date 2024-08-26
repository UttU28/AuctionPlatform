provider "azurerm" {
  features {}
}

data "azurerm_key_vault" "thiskeyvault" {
  name                = "thisdicekeyvault"
  resource_group_name = "thisresourcegroup"
}

data "azurerm_key_vault_secret" "general-location" {
  name         = "general-location"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

data "azurerm_key_vault_secret" "dicesaralapply-rg" {
  name         = "dicesaralapply-rg"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

data "azurerm_key_vault_secret" "webapp-name" {
  name         = "webapp-name"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

data "azurerm_key_vault_secret" "dicesaralapply-app-environment" {
  name         = "dicesaralapply-app-environment"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

data "azurerm_key_vault_secret" "dicesaralapply-log-analytics-workspace" {
  name         = "dicesaralapply-log-analytics-workspace"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

data "azurerm_key_vault_secret" "acrName" {
  name         = "acrName"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

data "azurerm_key_vault_secret" "acrPassword" {
  name         = "acrPassword"
  key_vault_id = data.azurerm_key_vault.thiskeyvault.id
}

# Define local variables to store the secret values
locals {
  general-location                    = data.azurerm_key_vault_secret.general-location.value
  dicesaralapply-rg                      = data.azurerm_key_vault_secret.dicesaralapply-rg.value
  webapp-name                    = data.azurerm_key_vault_secret.webapp-name.value
  dicesaralapply-app-environment         = data.azurerm_key_vault_secret.dicesaralapply-app-environment.value
  dicesaralapply-log-analytics-workspace = data.azurerm_key_vault_secret.dicesaralapply-log-analytics-workspace.value
  acrName                             = data.azurerm_key_vault_secret.acrName.value
  acrPassword                         = data.azurerm_key_vault_secret.acrPassword.value
  acrUrl                              = "${local.acrName}.azurecr.io/auctionplatform:latest"
}

