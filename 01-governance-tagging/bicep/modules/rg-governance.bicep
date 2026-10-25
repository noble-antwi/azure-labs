// Lab 01: everything scoped to the resource group.
//   P1  Modify  inherit costCenter from the resource group (with a managed identity)
//   P2  Deny    require costCenter
//   P3  Deny    require owner
//   lock        Delete (CanNotDelete) on the group
//   test vnet   optional, owner tag only

param location string
param useTagContributor bool
param deployTestVnet bool

var inheritTagDefinition = '/providers/Microsoft.Authorization/policyDefinitions/ea3f2387-9b95-492a-a190-fcdc54f7b070'
var requireTagDefinition = '/providers/Microsoft.Authorization/policyDefinitions/871b6d14-10aa-478d-b590-94f262ecfa99'

// Built-in role IDs (az role definition list --name ...)
var tagContributorRole = '4a9ae827-6dc8-4573-8ac7-8239d42aa03f'
var contributorRole = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
var p1Role = useTagContributor ? tagContributorRole : contributorRole

resource p1 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'lab01-p1-inherit-costcenter'
  location: location // where the system-assigned identity lives
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'P1 inherit costCenter (iac)'
    description: 'Lab 01 (governance-tagging), code build. Copies costCenter from the resource group onto any resource created or updated without one. Owner: noble.'
    policyDefinitionId: inheritTagDefinition
    enforcementMode: 'Default'
    parameters: {
      tagName: {
        value: 'costCenter'
      }
    }
  }
}

// The portal creates this role assignment for you on the Managed identity tab.
// In code it is a separate resource, which makes the role choice visible.
resource p1RoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, p1.id, p1Role)
  properties: {
    principalId: p1.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', p1Role)
    description: 'Lets P1 write tags during remediation.'
  }
}

// P2 and P3 are Deny rules: no identity, nothing to remediate.
resource p2 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'lab01-p2-require-costcenter'
  properties: {
    displayName: 'P2 require costCenter (iac)'
    description: 'Lab 01 (governance-tagging), code build. Blocks any new or updated resource in this group that has no costCenter tag. Works with P1, which copies costCenter from the resource group. Owner: noble.'
    policyDefinitionId: requireTagDefinition
    enforcementMode: 'Default'
    parameters: {
      tagName: {
        value: 'costCenter'
      }
    }
    nonComplianceMessages: [
      {
        message: 'Every resource in this group needs a costCenter tag. Add one, or leave it off and it is copied from the resource group automatically.'
      }
    ]
  }
}

resource p3 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'lab01-p3-require-owner'
  properties: {
    displayName: 'P3 require owner (iac)'
    description: 'Lab 01 (governance-tagging), code build. Blocks any new or updated resource in this group that has no owner tag. Nothing adds it automatically. Owner: noble.'
    policyDefinitionId: requireTagDefinition
    enforcementMode: 'Default'
    parameters: {
      tagName: {
        value: 'owner'
      }
    }
    nonComplianceMessages: [
      {
        message: 'Every resource in this group needs an owner tag with the name of the person responsible.'
      }
    ]
  }
}

resource lock 'Microsoft.Authorization/locks@2020-05-01' = {
  name: 'lock-no-delete'
  properties: {
    level: 'CanNotDelete'
    notes: 'Lab 01: blocks accidental deletion'
  }
}

// Created after the rules exist in the same deployment. Whether P1 has taken
// effect by then is part of the experiment: new assignments can take minutes.
resource testVnet 'Microsoft.Network/virtualNetworks@2024-05-01' = if (deployTestVnet) {
  name: 'vnet-iac-test'
  location: location
  tags: {
    owner: 'noble'
  }
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.20.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'default'
        properties: {
          addressPrefix: '10.20.0.0/24'
        }
      }
    ]
  }
  dependsOn: [
    p1
    p2
    p3
  ]
}

output p1PrincipalId string = p1.identity.principalId
output p1RoleName string = useTagContributor ? 'Tag Contributor' : 'Contributor'
