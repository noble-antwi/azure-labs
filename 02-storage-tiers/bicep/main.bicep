// Lab 02 storage tiers, rebuilt as code.
// Same choices as the portal build: keys off, anonymous off, TLS 1.2,
// a private container, both lifecycle rules, and read-only data access.

@description('Region. Defaults to the resource group region.')
param location string = resourceGroup().location

@description('Object ID of the person who gets Storage Blob Data Reader on the container. Passed at deploy time, never stored in the repo.')
param readerPrincipalId string

var tags = {
  environment: 'lab'
  purpose: 'lab'
  lab: 'storage-tiers'
  owner: 'noble'
  costCenter: 'it-lab'
  autoDelete: 'true'
}

// Built-in role: Storage Blob Data Reader
var blobDataReaderRoleId = '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'

// 1. The storage account (portal step 1, plus step 9: keys off)
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stlabtiersnoble02'
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    allowSharedKeyAccess: false
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

// 2. The hidden middle layer, then the private container (portal step 2)
resource blobSvc 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: sa
  name: 'default'
}

resource tiers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobSvc
  name: 'tiers'
  properties: {
    publicAccess: 'None'
  }
}

// 3. Lifecycle rules (portal steps 6 and 7). Same JSON as Code View.
//    The name must be 'default': an account has exactly one policy.
resource lifecycle 'Microsoft.Storage/storageAccounts/managementPolicies@2023-05-01' = {
  parent: sa
  name: 'default'
  properties: {
    policy: {
      rules: [
        {
          name: 'tier-by-age'
          enabled: true
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: [ 'blockBlob' ]
              prefixMatch: [ 'tiers/lc-' ]
            }
            actions: {
              baseBlob: {
                tierToCool: { daysAfterModificationGreaterThan: 30 }
                // the portal's "skip if rehydrated" box adds the second condition
                tierToArchive: {
                  daysAfterModificationGreaterThan: 180
                  daysAfterLastTierChangeGreaterThan: 7
                }
              }
            }
          }
        }
        {
          name: 'fast-demo'
          enabled: true
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: [ 'blockBlob' ]
              prefixMatch: [ 'tiers/lc' ]
            }
            actions: {
              baseBlob: {
                tierToCool: { daysAfterModificationGreaterThan: 1 }
                tierToCold: { daysAfterModificationGreaterThan: 2 }
                tierToArchive: { daysAfterModificationGreaterThan: 3 }
              }
            }
          }
        }
      ]
    }
  }
}

// 4. Read-only data access on the container only (portal step 10)
resource readerOnContainer 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: tiers
  name: guid(tiers.id, readerPrincipalId, blobDataReaderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobDataReaderRoleId)
    principalId: readerPrincipalId
    principalType: 'User'
  }
}

output accountName string = sa.name
