// 運営者情報。SITE_DESIGN.md ⑤「運営者表記の方針」参照。
// 本名・顔・店名は出さない。筆名「カイム」で統一し、Person構造化データの主体にする。
//
// TODO(カイムさん): 下記の未確定項目を埋めてください（意味は SITE_DESIGN.md ⑤ に説明あり）。
// - experienceYears: 板場に立って何年か
// - style: 業態（例: 「江戸前／おまかせ／カウンター〇席」）
// - region: 地域レベル（例: 「都内」「東京」）。店名・住所は出さない
// - overseasExperience: 海外経験（あれば。国と期間の粒度で）
// - qualifications: 資格（調理師免許・ふぐ調理師 等）
// - failureStory: 具体的な失敗談を1つ（経歴の羅列より信頼を作る）
// - noteUrl / xUrl: 実際のnote・XアカウントURL

export const authors = {
  kaimu: {
    id: 'kaimu',
    name: 'カイム',
    penName: true,
    workshopName: '鮨道編集室',
    jobTitle: '寿司職人',
    experienceYears: null as number | null, // TODO
    style: null as string | null, // TODO 例: "江戸前／おまかせ"
    region: null as string | null, // TODO 例: "都内"
    overseasExperience: null as string | null, // TODO
    qualifications: [] as string[], // TODO
    failureStory: null as string | null, // TODO
    bioShort:
      '現役の寿司職人。板場での実務を、技術・道具・キャリア・海外・経営の言葉で記録しています。',
    noteUrl: null as string | null, // TODO
    xUrl: null as string | null, // TODO
    avatarImage: null as string | null, // TODO: 手元写真 or 道具の写真
  },
} as const;

export type AuthorId = keyof typeof authors;
