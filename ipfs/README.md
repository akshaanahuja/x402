## 🎯 Overview

Run a local ipfs node and functions to post to ifps and retrieve from ipfs.

## Step 1
brew install ipfs
ipfs init
ipfs daemon

## Step 2
in your virtual environemnt that has pip installed, run 

pip install ipfs-api

so our Python program can talk to the IPFS node via its HTTP API.

## Step 3
Every CID you upload can be opened from any IPFS gateway URL:
https://ipfs.io/ipfs/<CID>

OR
From your terminal (with your IPFS daemon running):

ipfs cat QmdEAWmDx83mM3LQGgxBFYSXCG2L4HRDedtGYMNavybyYb


That prints your JSON directly to the terminal.

You can also download it to a file:

ipfs get QmdEAWmDx83mM3LQGgxBFYSXCG2L4HRDedtGYMNavybyYb -o result.json
cat result.json
