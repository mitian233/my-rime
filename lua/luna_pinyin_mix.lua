-- Only used by luna_pinyin_mix; existing schemas and global rime.lua are untouched.
local M = {}

function M.init(env)
  env.zh = Component.Translator(env.engine, "", "script_translator@zh_mix")
  env.jp = Component.Translator(env.engine, "", "script_translator@jp_mix")
  env.en = Component.Translator(env.engine, "", "table_translator@en_mix")
  env.t2s = Opencc("t2s.json")
end

function M.func(input, seg, env)
  if not seg:has_tag("abc") then return end

  local streams = {}
  for _, lang in ipairs({"zh", "jp", "en"}) do
    local translation = env[lang]:query(input, seg)
    if translation then
      -- Retain the translation for the lifetime of its iterator.
      local next_candidate, state, control = translation:iter()
      streams[lang] = {
        translation = translation,
        next = next_candidate,
        state = state,
        control = control,
      }
    end
  end

  local context = env.engine.context
  local priority = context:get_option("jp_priority") and "jp" or "zh"
  local secondary = priority == "zh" and "jp" or "zh"
  local order = {priority, secondary, "en"}
  local simplify = context:get_option("zh_simp")

  -- Reserve visible slots for each available language. Native ordering within
  -- each language is preserved; later candidates stay lazy for paging.
  while true do
    local emitted = false
    for _, lang in ipairs(order) do
      local stream = streams[lang]
      local quota = lang == priority and 3 or 1
      for _ = 1, quota do
        if not stream then break end
        local cand = stream.next(stream.state, stream.control)
        stream.control = cand
        if not cand then
          streams[lang] = nil
          break
        end
        local text = cand.text
        if lang == "zh" and simplify then
          text = env.t2s:convert(text)
        end
        -- Display the typed spelling rather than the translator's formatted
        -- pinyin/kana. Partial candidates cover only their own input range;
        -- Rime appends the remaining raw input when composing the preedit.
        cand:get_genuine().preedit = input:sub(1, cand._end - seg.start)
        yield(ShadowCandidate(cand, "luna_mix_" .. lang, text, "", false))
        emitted = true
      end
    end
    if not emitted then break end
  end
end

return M
