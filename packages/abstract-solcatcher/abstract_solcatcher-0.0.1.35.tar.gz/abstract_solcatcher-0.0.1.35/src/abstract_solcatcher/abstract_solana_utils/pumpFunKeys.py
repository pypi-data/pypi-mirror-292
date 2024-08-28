def get_instruction_map():
  return [{'instruction_number': '1', 'instruction_name': 'Mint', 'token_address': 'AkAUSJg1v9xYT3HUxdALH7NsrC6owmwoZuP9MLw8fxTL', 'token_name': '3CAT'}, {'instruction_number': '2', 'instruction_name': 'Mint Authority', 'token_address': 'TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM', 'token_name': 'Pump.fun Token Mint Authority'}, {'instruction_number': '3', 'instruction_name': 'Bonding Curve', 'token_address': '9nhxvNxfSUaJddVco6oa6NodtsCscqCScp6UU1hZkfGm', 'token_name': 'Pump.fun (3CAT) Bonding Curve'}, {'instruction_number': '4', 'instruction_name': 'Associated Bonding Curve', 'token_address': '889XLp3qvVAHpTYQmhn6cBpYSppV8Gi8E2Rgp9RH2vRy', 'token_name': 'Pump.fun (3CAT) Vault'}, {'instruction_number': '5', 'instruction_name': 'Global', 'token_address': '4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf', 'token_name': '4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf'}, {'instruction_number': '6', 'instruction_name': 'Mpl Token Metadata', 'token_address': 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s', 'token_name': 'Metaplex Token Metadata'}, {'instruction_number': '7', 'instruction_name': 'Metadata', 'token_address': 'CH41RxpjSXHqr1vfLTVYJMsfNs2fBCCWoAE13tPihXh7', 'token_name': 'CH41RxpjSXHqr1vfLTVYJMsfNs2fBCCWoAE13tPihXh7'}, {'instruction_number': '8', 'instruction_name': 'User', 'token_address': 'Fuy5MvbgzjSok1U8hH6mUY6WnLynzUextDxfEWMiTkn4', 'token_name': 'Fuy5MvbgzjSok1U8hH6mUY6WnLynzUextDxfEWMiTkn4'}, {'instruction_number': '9', 'instruction_name': 'System Program', 'token_address': '11111111111111111111111111111111', 'token_name': 'System Program'}, {'instruction_number': '10', 'instruction_name': 'Token Program', 'token_address': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'token_name': 'Token Program'}, {'instruction_number': '11', 'instruction_name': 'Associated Token Program', 'token_address': 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL', 'token_name': 'Associated Token Account Program'}, {'instruction_number': '12', 'instruction_name': 'Rent', 'token_address': 'SysvarRent111111111111111111111111111111111', 'token_name': 'Rent Program'}, {'instruction_number': '13', 'instruction_name': 'Event Authority', 'token_address': 'Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1', 'token_name': 'Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1'}, {'instruction_number': '14', 'instruction_name': 'Program', 'token_address': '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P', 'token_name': 'Pump.fun'}]
def get_pump_signature():
  return "dpL54KTyCPJQmm5cQmKm8nb38r9y7CGthR6D1CczTLMT5UvbxXwVy7FRzrCuHncJmGY6PqEjgiF8MTZg1YX1b7X"
def get_signature_js(signature=None):
  return {"signature":signature or get_pump_signature()}

def build_instructions_template(txnData,instruction_maps=None,printIt=False,saveIt=False):
  instruction_maps = instruction_maps or get_instruction_map()
  instructions = get_instructions_catalog(txnData,printIt=printIt,saveIt=saveIt)
  new_token_js = {}

  for j,instruction_map in enumerate(instruction_maps):
    addressType = instruction_map.get('instruction_name')
    address = instruction_map.get('token_address')
    instruction_maps[j]["catalog"]=[]
    found = False
    for instruction in instructions:
      inst_accounts = instruction.get('accounts')
      if address in inst_accounts:
        for i,inst_address in enumerate(inst_accounts):
          if inst_address == address:
            if found:
              if printIt:
                print(f"another catalog found for {address}")
            else:
              if printIt:
                print(f"#{j} - {addressType} FOUND")
            found = True
            if printIt:
              print(f"{addressType} found")
              print(f"event {instruction.get('events')}")
              print(f"accountKey {i}")
              print(f"programId {instruction.get('programId')}\n")
            instruction_maps[j]["catalog"].append({"index":i,"catalog":instruction})
    if found == False:
      print(f"#{addressType} NOT FOUND")
    j+=1
  return instruction_maps
def getPumpMap(signature = get_pump_signature()):
  txnData = getTransaction(signature=signature)
  instruction_maps = build_instructions_template(txnData,instruction_maps=None,printIt=False,saveIt=False)
  new_maps = []
  for instruction_map in instruction_maps:
    address = instruction_map.get('token_address')
    name = instruction_map.get('token_name')
    instruction_name = instruction_map.get('instruction_name')
    instruction_index = instruction_map.get('instruction_number')
    getEvent={}
    for catalogs in instruction_map.get('catalog'):
      account_index= catalogs.get('index')
      catalog = catalogs.get('catalog')
      events = catalog.get('events')
      accounts = catalog.get('accounts')
      if events:
        if accounts[account_index] == address:
          getEvent = {"event":events[0],"account":account_index,"address_type":instruction_name}
          if events[0] != 'Create':
            break
    new_maps.append(getEvent)
  return new_maps
def getTxnTypes(signature,maps=getPumpMap()):
  token_types = {}
  txnData = getTransaction(signature)
  instructions = get_instructions_catalog(txnData,printIt=False,saveIt=False)
  for new_map in maps:
    for instruction in instructions:
      if new_map.get('event') in instruction.get('events'):
        account = instruction.get('accounts')[new_map.get('account')]
        token_types[new_map.get('address_type')]=account
        break
  return token_types
