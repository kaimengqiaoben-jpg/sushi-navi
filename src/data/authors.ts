// 運営者情報。SITE_DESIGN.md ⑤「運営者表記の方針」参照。
//
// 2026-09-10 変更: 個人名（筆名含む）は一切出さない方針に確定。
// 「鮨道編集室」という屋号のみを運営主体として表記する。
// ※ただし「編集部」「編集チーム」のような複数人を思わせる表現は使わない
//   （実態は個人運営であることは隠さない。屋号=個人事業の名前、という位置付け）。
//
// 残りのTODO:
// - qualifications: 資格（調理師免許・ふぐ調理師 等）があれば
// - failureStory: 「大きな失敗はない」とのことなので空欄のまま。思い出したら追加可
// - xUrl: X（旧Twitter）アカウントがあれば
// - avatarImage: 手元・道具の写真（顔・個人が特定できるものは不可）

export const site = {
  entityName: '鮨道編集室',
  jobTitle: '寿司職人',
  experienceYears: 5 as number | null,
  style: '江戸前、カウンター8席' as string | null,
  region: '都内' as string | null,
  overseasExperience: null as string | null, // 海外経験なし
  qualifications: [] as string[], // TODO
  failureStory: null as string | null, // 「大きな失敗はない」とのこと
  bioShort:
    '現役の寿司職人が個人で運営しています。板場での実務を、技術・道具・キャリア・海外・経営の言葉で記録しています。',
  // note.com上で実際に記事を公開しているアカウント（プロフィール名は旧サイト名「寿司職人ナビ」のまま。
  // TODO: SUSHIDOブランドに合わせて更新すると導線が綺麗になる）
  noteUrl: 'https://note.com/modern_roses2643' as string | null,
  xUrl: null as string | null, // TODO
  avatarImage: null as string | null, // TODO: 手元写真 or 道具の写真（顔・個人が特定できるものは不可）
} as const;
