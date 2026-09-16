// 運営者情報。SITE_DESIGN.md ⑤「運営者表記の方針」参照。
//
// 2026-09-10: 個人名は一切出さない方針に確定 → 2026-09-16: 方針転換。
// ニックネーム「kaimu」で顔出し・本格的に出演する方針に変更。
// 本名・店名は引き続き出さない。屋号「鮨道編集室」はニックネームと併記する形で残す。
//
// 残りのTODO:
// - qualifications: 資格（調理師免許・ふぐ調理師 等）があれば
// - failureStory: 「大きな失敗はない」とのことなので空欄のまま。思い出したら追加可
// - xUrl: X（旧Twitter）アカウントがあれば
// - avatarImage: 顔写真・手元写真（顔出しOKになったので、プロフィール用の顔写真を優先して用意）

export const author = {
  name: 'kaimu',
  penName: true,
  showsFace: true, // 2026-09-16: 顔出しで出演する方針
  workshopName: '鮨道編集室',
  jobTitle: '寿司職人',
  experienceYears: 5 as number | null,
  style: '江戸前、カウンター8席' as string | null,
  region: '都内' as string | null,
  overseasExperience: null as string | null, // 海外経験なし
  qualifications: [] as string[], // TODO
  failureStory: null as string | null, // 「大きな失敗はない」とのこと
  bioShort:
    '現役の寿司職人「kaimu（かいむ）」。板場での実務を、技術・道具・キャリア・海外・経営の言葉で記録しています。',
  // note.com上で実際に記事を公開しているアカウント（プロフィール名は旧サイト名「寿司職人ナビ」のまま。
  // TODO: SUSHIDOブランドに合わせて更新すると導線が綺麗になる）
  noteUrl: 'https://note.com/modern_roses2643' as string | null,
  xUrl: null as string | null, // TODO
  avatarImage: null as string | null, // TODO: 顔写真を優先して用意（顔出しOK）
} as const;
