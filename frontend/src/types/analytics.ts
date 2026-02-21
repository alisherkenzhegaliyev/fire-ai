export interface DistributionBucket {
  label: string
  count: number
  percentage: number
}

export interface AnalyticsData {
  totalTickets: number
  totalManagers: number
  assignedCount: number
  unassignedCount: number
  bySegment: DistributionBucket[]
  byRequestType: DistributionBucket[]
  bySentiment: DistributionBucket[]
  byLanguage: DistributionBucket[]
  byOffice: DistributionBucket[]
  avgPriorityScore: number
}
