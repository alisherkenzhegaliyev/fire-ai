export type Position = 'Specialist' | 'SeniorSpecialist' | 'ChiefSpecialist'

export type Skill = 'VIP' | 'ENG' | 'KZ'

export interface Manager {
  id: string
  fullName: string
  position: Position
  skills: Skill[]
  businessUnit: string
  workload: number
  sessionId: string
}
