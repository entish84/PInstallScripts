#!/bin/bash

set -e

# 5. Inject 2026 Lua Configs
mkdir -p ~/.config/nvim/lua/plugins

# Config: Snacks (Git, Docker, Dashboard)
cat <<EOF > ~/.config/nvim/lua/plugins/snacks.lua
return {
  "folke/snacks.nvim",
  priority = 1000,
  lazy = false,
  opts = {
    dashboard = { enabled = true },
    lazygit = { enabled = true, configure = true },
    terminal = { enabled = true },
    notifier = { enabled = true },
  },
  keys = {
    { "<leader>gg", function() Snacks.lazygit() end, desc = "LazyGit" },
    { "<leader>kd", function() Snacks.terminal("lazydocker") end, desc = "LazyDocker" },
  },
}
EOF

# Config: C# & Docker LSP (using Roslyn and blink.cmp)
cat <<EOF > ~/.config/nvim/lua/plugins/lsp.lua
return {
  -- Enable LazyVim Extras for 2026
  { "LazyVim/LazyVim", opts = { extras = { "lang.dotnet", "lang.docker", "coding.blink" } } },

  -- Configure C# LSP (Roslyn)
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        roslyn = {
          -- Roslyn is the 2026 standard for C#
          enabled = true,
        },
        dockerls = {},
        docker_compose_language_service = {},
      },
    },
  },

  -- Ultra-fast 2026 Auto-completion
  {
    "saghen/blink.cmp",
    opts = {
      keymap = { preset = "super-tab" }, -- VSCode-like Tab completion
      completion = {
        menu = { draw = { treesitter = { "lsp" } } },
        documentation = { auto_show = true },
      },
    },
  },
}
EOF
