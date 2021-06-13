# Secure Plugin Managment System (SPMS) design for PQUIC

> This file contains the design of an implementation of the Secure Plugin Managment System (SPMS) as described in [1] for the PQUIC protocol.

## SPMS elements : Expected features

> This section summarizes all the features expected from each element of the SPMS according to [1].
>
> All the content is taken from `Section 3: Exchanging plugins` if it isn't explicitely stated otherwise.

### Plugin Developers
- write plugins and publish them on the PR.
- may be independent of the PQUIC implementers.
- monitor the validations published by PVs to ensure the tested plugins match the submitted code.

### Plugin Repository (PR)
- holds all protocol plugins from all developers.
- centralizes the secure communication between all participants.

### Plugin Validator (PV)
- validates the correct functioning of a plugin.
- can obtain the source code from developers willing to ease their validation.
- check that they are able to reproduce the submitted code
- serve the bytecodes of plugins they validated.
- Merkel Tree (MT) / Signed Root Tree (STR) :
	- builds a Merkle Prefix Tree [68] containing the plugins it successfully validated.
	- digitally signs its root [from the MT], forming a Signed Tree Root (STR).
	- The STR is sent to the PR. 
	- can build at most one tree per epoch. 
	-  When the PR is offline, the PVs can serve their own STRs.
	- plugin absence from the MT :
		- validation failed.
		- no validation took place at that epoch.
		- the failure cause is communicated to the PR.

### PQUIC Peers
- must provide evidence of plugin validity (before exchnaging plugins)
- can precisely express their required safety guarantees [using first order logic on PV requirements]

### Other
- the state of the wole system progresses on a discrete time scale defined by the epoch value.
	- At each epoch, plugins can be added or updated, and each PV can update their plugins validation.
	- epoch not yet defined (section B.1)
- allows expressing requirements in terms of PV approbation.
	- a PQUIC implementation can send a logical formula that expresses its required validation, e.g., `PV1 ∧ (PV2 ∨ PV3)`.
- [the] system is distributed. This makes PQUIC peers tolerant to participant failures.

## Ideas

### PR - PV communication
> The communication channels between the PR and the PV are currently under dev.
- [ ] Usage of publish-subscribe protocol (e.g. MQTT)
	- [ ] Broker embeded into PR
	- [ ] PV subscribes to PR verifier type (= MQTT topic)
	- [x] PR publishes plugin data :
		- ? plugin name, then PV pulls plugin code from PR at next epoch
		- ? plugin bytecode
		- ? binding (TODO : needs to defined format. binary ?)
		> First solution is kept because the PV pulling code is a hard requirement.
	- PV queue plugin data for verification at next epoch
- [ ] May send plugins on specific topics (multicast) or to all PVs
	- Interesting topics are : per verifier (T2, ...), per property (termination, memory check, ...) 
- [ ] mTLS is used over HTTP and MQTT to authenticate to PR on the PV side and the PVs on the PR side. No spurious PV will be able to communicate with the PR unless the CA's private key is leaked.

### PV architecture
- microservices architecture
	- scalable : horizontal scaling to handle PQUIC peers traffic (e.g. user gateway)
	- modular : easy to add new verifier since single API accessible
	- flexible : easy to change a part of the system as long as the APIs remain the same
	- if not kept, architecture may remain for monolithic implementation

#### Verifier service
##### Expected roles
- [x] Get bindings from Binding Manager and send them to the verifier
- [x] Post the result of the verification to the Binding Manager
- [x] The verifier in itself is stored in a separated container to allow specific configuration (see T2) and decouple it from the communication with other services
	- [x] The communication channel between the verifier and its controller is still to be defined 
		> currently the controller calls a python API interfacing the real verifier
- [x] May set 1 verifier per PV in a first time then deploy new PV with combination of frequently used verifiers (simplify lookup process on peer side)
	> The verifier selection and the configuration of the containers stack are made at deployement time through a single configuration file for the entire PV
##### Possible issues
- The python interface is currenlty untested with real verifiers, there are just 2 dummy (python) verifiers returning a successful or failing result for each binding
- The received binding format may be inappropriate for real verifiers

#### Binding Manager service
##### Expected roles
- [ ] Pull bindings from PR
	> This role is delegated the the new PR gateway service
- [x] Store bindings in a "db" (e.g. JSON store) and the result of each verifier
	- The current "db" is a python hashmap protected by read/write locks
- [ ] If the result of a verification is a failure, it post it to the PR
	> The communication channels between the PR and the PV are currently under dev.
- [x] On validate, it returns bindings validated by all the verifiers
	- A first order logic expression is evaluated on each plugin's results to return the validated ones. The expression is provided in the config file required for the PV's deployment.
- [ ] Is able to provide the binding corresponding to a plugin name (maybe the parsed version ?)
	> Currently this feature is delegated to the Merkle Tree Manager
###### Possible issues
- The current backend db implementation may be unapropriate for high binding arrival rate due to its simple locking scheme (1 lock protecting the whole structure for writes).
	- It may be more interesting to use other synchronization mechanisms for highly concurrent systems.
	- It could alsoe be more interesting to use appropriate db like CouchDB or MariaDB

#### Merkel Tree Manager service
##### Expected roles
- [X] Pull validated plugins from Binding Manager
- [x] Build the MT
- [x] Generate the STR 
- [ ] Post the STR to the PR
	> The communication channels between the PR and the PV are currently under dev.
- [ ] Provide API for path lookups (dev and user), binding and STR service
	> Currently the dev lookup is not implemented
##### Possible issues
- The returned format for lookups is currently inapropriate when there are plugin names conflicts. 
The implementation returns an array with the other hashes of the leaf but we don't know in which order we have to concatenate all the hashes.
- The STR currently only contains the root hash, some metadata like the epoch might be needed
- Binding duplication between the Merkle Tree leaves and the Binding Manager backend
	- Important to keep the bindings in the BM backend because the MT is rebuild from scratch at each epoch
	- Maybe find a way to only keep hashes in the tree and let the bindings in the BM manager => bindings retrieval left to BM manager then rather than to the MT manager.
- Currently the epoch is still undefined, a simple sleep is used

#### User Gateway service
- [x] Provide isolation between inner APIs and outer world
- [ ] May be used to cache frequent path
	> Currenlty unimplemented synchronization issues may happen with the epoch

## References 
[1] `De Coninck, Q., Michel, F., Piraux, M., Rochet, F., Given-Wilson, T., Legay, A., ... & Bonaventure, O. (2019). Pluginizing quic. In Proceedings of the ACM Special Interest Group on Data Communication (pp. 59-74).`
