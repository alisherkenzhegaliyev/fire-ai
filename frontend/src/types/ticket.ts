export type RequestType =
  | 'Complaint'
  | 'DataChange'
  | 'Consultation'
  | 'Claim'
  | 'AppMalfunction'
  | 'FraudulentActivity'
  | 'Spam'

export type Sentiment = 'Positive' | 'Neutral' | 'Negative'

export type Language = 'KZ' | 'ENG' | 'RU'

export type Segment = 'Mass' | 'VIP' | 'Priority'

export interface Ticket {
  id: string
  customerGuid: string
  gender: string
  dateOfBirth: string
  segment: Segment
  description: string
  attachments: string
  country: string
  region: string
  city: string
  street: string
  buildingNumber: string
  latitude: number | null
  longitude: number | null
  // NLP enrichment
  requestType: RequestType
  sentiment: Sentiment
  priorityScore: number
  language: Language
  summary: string
  // Assignment
  assignedManagerId: string | null
  assignedManagerName: string | null
  assignedOfficeId: string | null
  assignedOfficeName: string | null
  sessionId: string
  createdAt: string
}
