# Shared modules

Bicep modules reused across labs. Import with a relative path:

```bicep
module network '../modules/network.bicep' = {
  name: 'network'
  params: {
    vnetName: 'vnet-lab'
    addressSpace: '10.0.0.0/16'
  }
}
```

Keep modules parameterised and free of lab-specific names. A module earns its
place here once a second lab needs it — don't abstract on the first use.
