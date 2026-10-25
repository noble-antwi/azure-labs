// Lab 01: governance and tagging, rebuilt as code.
// Deploys at SUBSCRIPTION scope because two things live there:
//   - the resource group itself
//   - P4, the allowed-locations rule (assigned to the whole subscription)
// Everything scoped to the resource group (P1-P3, P1's role, the lock, a test
// network) is in modules/rg-governance.bicep.
//
// Deploy:
//   az deployment sub create --location eastus --template-file main.bicep

targetScope = 'subscription'

@description('Region for the resource group and P1\'s managed identity.')
param location string = 'eastus'

@description('Name of the resource group to build.')
param rgName string = 'rg-lab-governance-tagging-iac'

@description('Tags on the resource group. costCenter is what P1 copies down.')
param rgTags object = {
  costCenter: 'it-lab'
  owner: 'noble'
  environment: 'lab'
  purpose: 'lab'
  lab: 'governance-tagging'
  autoDelete: 'true'
}

@description('Give P1\'s identity Tag Contributor (least privilege) instead of the Contributor the definition asks for.')
param useTagContributor bool = true

@description('Also deploy P4 at subscription scope. The portal build already has one; two identical Deny rules are harmless.')
param deployP4 bool = true

@description('Deploy a test network with only an owner tag, to see whether P1 adds costCenter.')
param deployTestVnet bool = true

// Built-in definition IDs, looked up with az policy definition list.
// They are the same in every tenant.
var allowedLocationsDefinition = '/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: rgTags
}

module governance 'modules/rg-governance.bicep' = {
  name: 'lab01-rg-governance'
  scope: rg
  params: {
    location: location
    useTagContributor: useTagContributor
    deployTestVnet: deployTestVnet
  }
}

resource p4 'Microsoft.Authorization/policyAssignments@2024-04-01' = if (deployP4) {
  name: 'lab01-p4-eastus-only-iac'
  properties: {
    displayName: 'P4 eastus only (iac)'
    description: 'Lab 01 (governance-tagging), code build. Blocks any new or updated resource in this subscription outside East US. Resource groups and global resources are not checked. Owner: noble.'
    policyDefinitionId: allowedLocationsDefinition
    enforcementMode: 'Default'
    parameters: {
      listOfAllowedLocations: {
        value: [
          'eastus'
        ]
      }
    }
    nonComplianceMessages: [
      {
        message: 'Resources in this subscription must be created in East US. Pick East US as the region, or ask the subscription owner (noble) to approve another region.'
      }
    ]
  }
}

output resourceGroupId string = rg.id
output p1PrincipalId string = governance.outputs.p1PrincipalId
output p1RoleName string = governance.outputs.p1RoleName
