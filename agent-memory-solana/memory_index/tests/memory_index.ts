import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MemoryIndex } from "../target/types/memory_index";
import { expect } from "chai";
import { PublicKey } from "@solana/web3.js";
import { MemoryIndexClient, createMemoryIndexClient } from "../src/client";

describe("memory_index", () => {
  // Configure the client to use the local cluster.
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.memoryIndex as Program<MemoryIndex>;

  let testCid: string;
  let testTags: string[];

  beforeEach(() => {
    testCid = "QmYjtig7VJQ6XsnUjqqJvj7QaMcCAwtrgNdahSiFofrE7o";
    testTags = ["python", "testing", "agent"];
  });

  it("Stores a memory successfully", async () => {
    const authority = provider.wallet.publicKey;
    const [memoryPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("memory"), authority.toBuffer(), Buffer.from(testCid)],
      program.programId
    );

    const tx = await program.methods
      .storeMemory(testCid, testTags)
      .rpc();

    console.log("Store memory transaction signature", tx);

    // Fetch the stored memory
    const memoryAccount = await program.account.memoryIndex.fetch(memoryPda);

    expect(memoryAccount.cid).to.equal(testCid);
    expect(memoryAccount.tags).to.deep.equal(testTags);
    expect(memoryAccount.authority.toBase58()).to.equal(authority.toBase58());
  });

  it("Fails to store memory with CID too long", async () => {
    const longCid = "Qm".repeat(60); // 120 chars, exceeding 100 char limit

    try {
      await program.methods
        .storeMemory(longCid, testTags)
        .rpc();

      expect.fail("Should have thrown an error");
    } catch (err) {
      expect(err.error.errorMessage).to.include("CID is too long");
    }
  });

  it("Fails to store memory with too many tags", async () => {
    const manyTags = Array(25).fill("tag"); // 25 tags, exceeding 20 tag limit

    try {
      await program.methods
        .storeMemory(testCid, manyTags)
        .rpc();

      expect.fail("Should have thrown an error");
    } catch (err) {
      expect(err.error.errorMessage).to.include("Too many tags");
    }
  });

  it("Fails to store memory with tag too long", async () => {
    const longTag = "a".repeat(60); // 60 chars, exceeding 50 char limit
    const tagsWithLongTag = ["python", longTag];

    try {
      await program.methods
        .storeMemory(testCid, tagsWithLongTag)
        .rpc();

      expect.fail("Should have thrown an error");
    } catch (err) {
      expect(err.error.errorMessage).to.include("Tag is too long");
    }
  });

  it("Gets memories by tag using client", async () => {
    // First, store some memories with different tags
    await program.methods
      .storeMemory("QmCID1QueryByTag", ["python", "agent"])
      .rpc();

    await program.methods
      .storeMemory("QmCID2QueryByTag", ["rust", "agent"])
      .rpc();

    await program.methods
      .storeMemory("QmCID3QueryByTag", ["typescript", "web"])
      .rpc();

    // Use the client to query by tag
    const client = createMemoryIndexClient(provider, program);
    const pythonMemories = await client.getMemoriesByTag("python");
    const agentMemories = await client.getMemoriesByTag("agent");
    const webMemories = await client.getMemoriesByTag("web");

    // Should have at least the memories we just created
    expect(pythonMemories.length).to.be.at.least(1);
    expect(pythonMemories.some((m) => m.cid === "QmCID1QueryByTag")).to.be.true;

    expect(agentMemories.length).to.be.at.least(2); // Both memory1 and memory2 have "agent" tag
    expect(agentMemories.some((m) => m.cid === "QmCID1QueryByTag")).to.be.true;
    expect(agentMemories.some((m) => m.cid === "QmCID2QueryByTag")).to.be.true;

    expect(webMemories.length).to.be.at.least(1);
    expect(webMemories.some((m) => m.cid === "QmCID3QueryByTag")).to.be.true;
  });

  it("Stores multiple memories with different tags", async () => {
    const authority = provider.wallet.publicKey;
    const memories = [
      {
        cid: "QmYjtig7VJQ6XsnUjqqJvj7QaMcCAwtrgNdahSiFofrE7o",
        tags: ["python", "agent"]
      },
      {
        cid: "QmHash2AnotherCIDHereForTestingPurposes",
        tags: ["rust", "blockchain"]
      },
      {
        cid: "QmYetAnotherTestCIDForMemoryStorage",
        tags: ["typescript", "web", "agent"]
      },
    ];

    for (const memory of memories) {
      const [memoryPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("memory"), authority.toBuffer(), Buffer.from(memory.cid)],
        program.programId
      );

      await program.methods
        .storeMemory(memory.cid, memory.tags)
        .rpc();

      // Verify each memory was stored correctly
      const account = await program.account.memoryIndex.fetch(memoryPda);
      expect(account.cid).to.equal(memory.cid);
      expect(account.tags).to.deep.equal(memory.tags);
      expect(account.authority.toBase58()).to.equal(authority.toBase58());
    }

    console.log("Successfully stored", memories.length, "memories");
  });
});
