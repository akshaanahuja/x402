use anchor_lang::prelude::*;

declare_id!("6dLHMacUJMThKeCwCzZRTLy9qfA1fwzoPXSYNy4CHEAE");

#[program]
pub mod memory_index {
    use super::*;

    pub fn store_memory(
        ctx: Context<StoreMemory>,
        cid: String,
        tags: Vec<String>,
    ) -> Result<()> {
        let memory = &mut ctx.accounts.memory;
        
        // Validate CID length (IPFS CIDs are typically less than 100 chars)
        require!(cid.len() <= 100, ErrorCode::CidTooLong);
        
        // Validate tags
        require!(tags.len() <= 20, ErrorCode::TooManyTags);
        for tag in &tags {
            require!(tag.len() <= 50, ErrorCode::TagTooLong);
        }
        
        memory.cid = cid;
        memory.tags = tags;
        memory.timestamp = Clock::get()?.unix_timestamp;
        memory.authority = ctx.accounts.authority.key();
        
        msg!("Memory stored: cid={}, tags={:?}", memory.cid, memory.tags);
        Ok(())
    }

    pub fn initialize(_ctx: Context<Initialize>) -> Result<()> {
        msg!("Memory Index Program initialized");
        Ok(())
    }
}

#[account]
pub struct MemoryIndex {
    pub cid: String,
    pub tags: Vec<String>,
    pub timestamp: i64,
    pub authority: Pubkey,
}

impl MemoryIndex {
    // Calculate space: 8 discriminator + fields
    pub const SPACE: usize = 8 + // discriminator
        4 + 100 + // cid (String with max len)
        4 + (4 + 50) * 20 + // tags (Vec with max 20 items, each String max 50)
        8 + // timestamp
        32; // authority
}

#[derive(Accounts)]
#[instruction(cid: String)]
pub struct StoreMemory<'info> {
    #[account(
        init,
        payer = authority,
        space = MemoryIndex::SPACE,
        seeds = [b"memory", authority.key().as_ref(), cid.as_bytes()],
        bump
    )]
    pub memory: Account<'info, MemoryIndex>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Initialize {}

#[error_code]
pub enum ErrorCode {
    #[msg("CID is too long, maximum 100 characters")]
    CidTooLong,
    #[msg("Too many tags, maximum 20 tags")]
    TooManyTags,
    #[msg("Tag is too long, maximum 50 characters")]
    TagTooLong,
}
