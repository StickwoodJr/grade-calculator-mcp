import React from 'react';
import { CourseData, calculateCourse } from '../utils/calculator';
import { AlertCircle, Calendar, FileText } from 'lucide-react';

interface CourseSpreadsheetProps {
  course: CourseData;
  onUpdateScore: (courseCode: string, itemId: string, earnedPoints: number | null) => void;
  onUpdateStatus: (courseCode: string, itemId: string, status: "Not Started" | "In Progress" | "Done") => void;
}

export const CourseSpreadsheet: React.FC<CourseSpreadsheetProps> = ({
  course,
  onUpdateScore,
  onUpdateStatus
}) => {
  const calc = calculateCourse(course);

  return (
    <div className="space-y-6">
      {/* Course Header Banner */}
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-black text-slate-900 dark:text-white">
              {course.course_code}
            </h2>
            <span className="text-sm font-semibold text-slate-500">
              {course.course_name}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 flex items-center gap-2">
            <span>{course.credits} Credits</span> •
            <span>{course.is_technical ? 'Technical Computing Core' : (course.grading_type === 'sat_un' ? 'Co-op Prep (Pass/Fail)' : 'General Elective')}</span> •
            <span>Scale: {course.grade_scale}</span>
          </p>
          {course.passing_criteria && (
            <div className="mt-2 text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/50 p-2 rounded border border-slate-200 dark:border-slate-700">
              <span className="font-semibold">Passing Requirements: </span>
              {course.passing_criteria.join(' • ')}
            </div>
          )}
        </div>

        {/* Live Course KPIs */}
        <div className="flex items-center gap-3">
          <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center min-w-[90px]">
            <span className="text-[10px] uppercase font-bold text-slate-400">Completed</span>
            <div className="text-lg font-bold text-slate-800 dark:text-slate-100">
              {calc.completed_weight.toFixed(1)}%
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center min-w-[90px]">
            <span className="text-[10px] uppercase font-bold text-slate-400">Current Avg</span>
            <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {calc.current_average !== null ? `${calc.current_average.toFixed(1)}%` : '—'}
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center min-w-[90px]">
            <span className="text-[10px] uppercase font-bold text-slate-400">Projected</span>
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {calc.projected_final.toFixed(1)}%
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-700 text-center min-w-[80px]">
            <span className="text-[10px] uppercase font-bold text-slate-400">Grade</span>
            <div className="text-lg font-black text-slate-900 dark:text-white">
              {calc.letter_grade}
            </div>
          </div>
        </div>
      </div>

      {/* Hurdle Warnings if any */}
      {calc.hurdle_warnings.length > 0 && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-sm">Hurdle Warning Active</h4>
            <ul className="text-xs list-disc list-inside mt-1 space-y-0.5">
              {calc.hurdle_warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Spreadsheet Grid */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700 text-sm">
            <thead className="bg-slate-800 text-white text-xs font-semibold">
              <tr>
                <th className="px-4 py-3 text-left">Category</th>
                <th className="px-4 py-3 text-left">Assessment Item</th>
                <th className="px-3 py-3 text-right">Weight %</th>
                <th className="px-3 py-3 text-right">Max Pts</th>
                <th className="px-4 py-3 text-right w-28 bg-slate-900 text-amber-300">Earned Pts</th>
                <th className="px-3 py-3 text-right">Score %</th>
                <th className="px-3 py-3 text-right">Weighted %</th>
                <th className="px-3 py-3 text-center">Due Date</th>
                <th className="px-4 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700/50">
              {course.categories.map(cat => {
                return (
                  <React.Fragment key={cat.category_id}>
                    {/* Category Header Row */}
                    <tr className="bg-slate-100/70 dark:bg-slate-900/40 text-xs font-bold text-slate-700 dark:text-slate-300">
                      <td colSpan={2} className="px-4 py-2 flex items-center gap-2">
                        <FileText className="w-3.5 h-3.5 text-blue-600" />
                        {cat.name}
                        {cat.hurdle_description && (
                          <span className="text-[11px] font-normal text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30 px-2 py-0.5 rounded">
                            {cat.hurdle_description}
                          </span>
                        )}
                      </td>
                      <td className="px-3 py-2 text-right font-mono font-bold text-blue-600 dark:text-blue-400">
                        {cat.weight_percent.toFixed(1)}%
                      </td>
                      <td colSpan={6}></td>
                    </tr>

                    {/* Item Rows */}
                    {cat.items.map(item => {
                      const hasEarned = item.earned_points !== null && !isNaN(item.earned_points);
                      const scorePct = hasEarned ? (item.earned_points! / item.max_points) * 100 : null;
                      const weightedPct = hasEarned ? (scorePct! / 100) * item.weight_percent : null;

                      return (
                        <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition">
                          <td className="px-4 py-2.5 text-xs text-slate-400">
                            {cat.name}
                          </td>
                          <td className="px-4 py-2.5 font-medium text-slate-800 dark:text-slate-200">
                            {item.name}
                          </td>
                          <td className="px-3 py-2.5 text-right font-mono text-slate-500">
                            {item.weight_percent.toFixed(1)}%
                          </td>
                          <td className="px-3 py-2.5 text-right font-mono text-slate-500">
                            {item.max_points}
                          </td>
                          <td className="px-3 py-1.5 text-right bg-amber-50/40 dark:bg-amber-950/10">
                            <input
                              type="number"
                              min="0"
                              max={item.max_points * 1.5}
                              step="any"
                              placeholder="—"
                              value={item.earned_points !== null ? item.earned_points : ''}
                              onChange={(e) => {
                                const val = e.target.value === '' ? null : parseFloat(e.target.value);
                                onUpdateScore(course.course_code, item.id, val);
                              }}
                              className="w-20 px-2 py-1 text-right font-mono font-bold bg-white dark:bg-slate-900 border border-amber-300 dark:border-amber-700/60 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-900 dark:text-white"
                            />
                          </td>
                          <td className="px-3 py-2.5 text-right font-mono font-semibold text-slate-700 dark:text-slate-300">
                            {scorePct !== null ? `${scorePct.toFixed(1)}%` : '—'}
                          </td>
                          <td className="px-3 py-2.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                            {weightedPct !== null ? `${weightedPct.toFixed(2)}%` : '—'}
                          </td>
                          <td className="px-3 py-2.5 text-center text-xs text-slate-500">
                            {item.due_date ? (
                              <span className="inline-flex items-center gap-1">
                                <Calendar className="w-3 h-3 text-slate-400" />
                                {item.due_date}
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>
                          <td className="px-4 py-2 text-center">
                            <select
                              value={item.status}
                              onChange={(e) => onUpdateStatus(course.course_code, item.id, e.target.value as any)}
                              className={`text-xs px-2 py-1 rounded font-medium border ${
                                item.status === 'Done'
                                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                                  : item.status === 'In Progress'
                                  ? 'bg-blue-50 text-blue-800 border-blue-300 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800'
                                  : 'bg-slate-50 text-slate-600 border-slate-300 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                              }`}
                            >
                              <option value="Not Started">Not Started</option>
                              <option value="In Progress">In Progress</option>
                              <option value="Done">Done</option>
                            </select>
                          </td>
                        </tr>
                      );
                    })}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
