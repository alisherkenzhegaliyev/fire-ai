import { Badge } from "../shared/Badge";
import type { Manager } from "../../types/manager";

interface ManagersTableProps {
  managers: Manager[];
}

const POSITION_LABELS: Record<string, string> = {
  Specialist: "Spec.",
  SeniorSpecialist: "Sr. Spec.",
  ChiefSpecialist: "Chief Spec.",
};

export function ManagersTable({ managers }: ManagersTableProps) {
  const maxWorkload = Math.max(...managers.map((m) => m.workload), 1);

  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700/50">
        <p className="text-sm font-semibold text-white">
          Managers ({managers.length})
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700/50 text-xs text-gray-400 uppercase tracking-wider">
              <th className="px-4 py-2.5 text-left font-medium">Name</th>
              <th className="px-4 py-2.5 text-left font-medium">Position</th>
              <th className="px-4 py-2.5 text-left font-medium">Skills</th>
              <th className="px-4 py-2.5 text-left font-medium">Office</th>
              <th className="px-4 py-2.5 text-left font-medium min-w-[140px]">
                Workload
              </th>
            </tr>
          </thead>
          <tbody>
            {managers.map((manager) => {
              const pct = Math.round((manager.workload / maxWorkload) * 100);
              return (
                <tr key={manager.id} className="border-b border-gray-700/30">
                  <td className="px-4 py-2.5 font-medium text-gray-200">
                    {manager.fullName}
                  </td>
                  <td className="px-4 py-2.5 text-gray-400 text-xs">
                    {POSITION_LABELS[manager.position] ?? manager.position}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex flex-wrap gap-1">
                      {manager.skills.map((skill) => (
                        <Badge key={skill} value={skill} />
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-gray-300 text-xs truncate max-w-[120px]">
                    {manager.businessUnit}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 rounded-full bg-gray-700 h-1.5 overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 transition-all"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-6 text-right">
                        {manager.workload}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
            {managers.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-8 text-center text-sm text-gray-500"
                >
                  No managers found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
