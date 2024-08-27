# Oasees SDK

The OASEES SDK is a Python package that consists of two modules: the **Command Line Interface (CLI)** module and the **Python Environment** module.

***

## CLI

The CLI module's purpose is to handle the Kubernetes aspect of the OASEES framework. It provides the user with a few simple commands to quickly provision and configure a Kubernetes cluster, as well as automate and facilitate its nodes' connection to the OASEES blockchain
<br>

### <u>Installation</u>
Like any other user Python package published on the PyPi repository, the user can install the OASEES SDK using pip.

<ol>
<li>

Ensure that pip is present on your machine. If not, install it:
    
    sudo apt install python3-pip

</li>

<li>

Install with pip:

    pip install oasees_sdk

</li>

<li>

Set up the CLI module for use by adding its installation folder to your system's PATH (**example for Ubuntu**):
    
    export PATH="/home/{USERNAME}/.local/bin:$PATH"

And make sure that its running properly by executing:

    oasees-sdk

Which will also provide you with the CLI's available commands and a very short description for each one.

<br>

**NOTE:** An extended description for each of the CLI's commands can be provided by executing:

    oasees-sdk [COMMAND] --help

</li>

</ol>

<br>

### <u>Usage</u>

**<u>Important:</u>** Before starting to use the CLI module, **ensure that an instance of the OASEES stack is up and running.**

The SDK is designed to work in parallel with the rest of the stack and before provisioning a cluster, <u>the user will be prompted to enter the stack's IP address and their blockchain account information</u> (if you're using a test account, make sure it's the same one that you've imported on MetaMask).

Should any typing mistake happen during the input prompts, you can edit the configuration file located in 
`/home/{username}/.oasees_sdk/config.json`, or use `oasees-sdk config-full-reset` to completely reset the configuration and force the prompts to reappear.

<br>

The CLI's typical flow of usage can be described with the following steps:

<ol>

<li>

Install the OASEES SDK on all the machines that will participate in the cluster (**both the master node and the worker nodes**) using the installation commands mentioned above.

</li>

<br>

<li>

Provision a K3S Cluster on the machine that represents the cluster's master node:

    oasees-sdk init-cluster

The cluster should be visible on your Portal's home page almost immediately.
</li>

<br>

<li>

Retrieve your cluster's token:

    oasees-sdk get-token

</li>

<br>

<li>

Execute the join-cluster command **on each of your worker devices** to join them with your cluster, providing the master's IP address and the retrieved token.

    oasees-sdk join-cluster --ip {K3S_MASTER_IP_ADDRESS} --token {K3S_MASTER_TOKEN}


</li>

<br>

<li>

Execute the register-new-nodes command **on your master node** to create blockchain accounts for each of your unregistered worker devices, register them to the blockchain and associate them with your cluster.

    oasees-sdk register-new-nodes

**NOTE:** This command detects and handles only the nodes that aren't already registered on the blockchain, so you can use it multiple times as you scale your K3S Cluster with new devices / nodes.

</li>

<br>

<li>

If you intend to associate your cluster with a blockchain DAO, execute the apply-dao-logic command, providing the IPFS hash of your uploaded DAO contracts.

    oasees-sdk apply-dao-logic {DAO_CONTRACTS_IPFS_HASH}

After the DAO logic is applied, devices that are already registered on the blockchain, as well as devices that get registered at a later point, will automatically be able to perform DAO actions such as creating proposals and voting.

</li>

<br>

Launching a Jupyter Notebook or a Python shell (**both of which can be found) :

    from oasees_sdk import oasees_sdk
    

The CLI module's purpose is to handle the Kubernetes aspect of the OASEES framework. It provides the user with a few simple commands to quickly provision and configure a Kubernetes cluster, as well as connect it to the OASEES blockchain 

The SDK is embedded into the Jupyter Notebook image which is built upon the creation of the Oasees Stack. This means that no installation of the SDK and its requirements is needed from the user's side. It only needs to be imported either into a Jupyter Notebook or Python Console by running:
```
import oasees_sdk
```
<br/>

Or in the stack's Jupyter Terminal (all three options are found in the portal's <i>Notebook</i> tab), where you first need to launch the python shell by running:
```
python3
```
And then import the oasees_sdk.

<br/>


## Usage / Instructions (outdated)
As soon as the SDK gets successfully imported into the chosen python environment, the following brief documentation about its functions and their usage is printed: