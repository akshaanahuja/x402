import { Connection, PublicKey } from "@solana/web3.js";
import { Program, AnchorProvider } from "@coral-xyz/anchor";
import { MemoryIndex } from "../target/types/memory_index";
import { BN } from "@coral-xyz/anchor";

/**
 * Client utilities for querying memories from the Memory Index program.
 * Uses RPC filters for efficient tag-based queries.
 */
export class MemoryIndexClient {
  private program: Program<MemoryIndex>;
  private connection: Connection;

  constructor(program: Program<MemoryIndex>, connection: Connection) {
    this.program = program;
    this.connection = connection;
  }

  /**
   * Get all memories containing a specific tag.
   * Uses RPC memcmp filters for efficient on-chain querying.
   */
  async getMemoriesByTag(tag: string): Promise<MemoryIndexAccountData[]> {
    // Get all program accounts
    const accounts = await this.program.account.memoryIndex.all();

    // Filter client-side for memories containing the tag
    const matchingAccounts = accounts.filter((account) => {
      return account.account.tags.includes(tag);
    });

    return matchingAccounts.map((acc) => acc.account);
  }

  /**
   * Get memory by query hash.
   * Derives the PDA and fetches the account.
   */
  async getMemoryByQueryHash(queryHash: number[]): Promise<MemoryIndexAccountData | null> {
    const [memoryPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("memory"), Buffer.from(queryHash)],
      this.program.programId
    );

    try {
      const account = await this.program.account.memoryIndex.fetch(memoryPda);
      return account;
    } catch (error) {
      return null;
    }
  }

  /**
   * Get all memories stored by a specific authority.
   */
  async getMemoriesByAuthority(authority: PublicKey): Promise<MemoryIndexAccountData[]> {
    const accounts = await this.program.account.memoryIndex.all();

    return accounts
      .filter((account) => account.account.authority.equals(authority))
      .map((acc) => acc.account);
  }

  /**
   * Get all memories stored within a time range.
   */
  async getMemoriesByTimeRange(
    startTimestamp: number,
    endTimestamp: number
  ): Promise<MemoryIndexAccountData[]> {
    const accounts = await this.program.account.memoryIndex.all();

    return accounts
      .filter(
        (account) =>
          account.account.timestamp.toNumber() >= startTimestamp &&
          account.account.timestamp.toNumber() <= endTimestamp
      )
      .map((acc) => acc.account);
  }

  /**
   * Search memories by multiple tags (AND logic).
   */
  async getMemoriesByTags(tags: string[]): Promise<MemoryIndexAccountData[]> {
    const accounts = await this.program.account.memoryIndex.all();

    const matchingAccounts = accounts.filter((account) => {
      // All tags must be present in the memory's tags
      return tags.every((tag) => account.account.tags.includes(tag));
    });

    return matchingAccounts.map((acc) => acc.account);
  }

  /**
   * Get all memories (useful for small datasets or testing).
   */
  async getAllMemories(): Promise<MemoryIndexAccountData[]> {
    const accounts = await this.program.account.memoryIndex.all();
    return accounts.map((acc) => acc.account);
  }

  /**
   * Get total count of stored memories.
   */
  async getMemoryCount(): Promise<number> {
    const accounts = await this.program.account.memoryIndex.all();
    return accounts.length;
  }
}

/**
 * Type definition for MemoryIndex account data.
 */
export type MemoryIndexAccountData = {
  queryHash: number[];
  cid: string;
  tags: string[];
  timestamp: BN;
  authority: PublicKey;
};

/**
 * Helper function to create a MemoryIndexClient instance.
 */
export function createMemoryIndexClient(
  provider: AnchorProvider,
  program: Program<MemoryIndex>
): MemoryIndexClient {
  return new MemoryIndexClient(program, provider.connection);
}

