import React, { useState } from 'react';
import { CourseData, calculateCourse, calculateWhatIf, getSenecaLetterGrade } from '../utils/calculator';
import { Sparkles, Calculator } from 'lucide-react';

interface WhatIfSimulatorProps {
  courses: CourseData[];
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({ courses }) => {
  const eligibleCourses = courses.filter(c => c.grading_type === 'percentage_gpa');
  const [selectedCode, setSelectedCode] = useState<string>(eligibleCourses[0]?.course_code || '');
  const [targetGrade, setTargetGrade] = useState<string>('A');
  const [hypotheticalRemainingScore, setHypotheticalRemainingScore] = useState<number>(85);

  const selectedCourse = courses.find(c => c.course_code === selectedCode);
  const calc = selectedCourse ? calculateCourse(selectedCourse) : null;

  const targetPercentageMap: Record<string, number> = {
    'A+': 90,
    'A': 80,
    'B+': 75,
    'B': 70,
    'C+': 65,
    'C': 60,
    'D+': 55,
    'D': 50
  };

  const targetPct = targetPercentageMap[targetGrade] || 80;
  const whatIfResult = calc ? calculateWhatIf(calc, targetPct) : null;

  // Compute hypothetical final grade with slider
  const hypotheticalFinal = calc
    ? Math.min(100, Math.max(0, calc.earned_weight + (whatIfResult?.remainingWeight || 0) * (hypotheticalRemainingScore / 100)))
    : 0;
  const hypotheticalLetter = getSenecaLetterGrade(hypotheticalFinal, false);

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Target Grade Solver & "What-If" Scenario Simulator
            </h2>
            <p className="text-xs text-slate-500">
              Calculate the exact score needed on remaining deliverables or simulate final exam scenarios
            </p>
          </div>
        </div>

        {/* Course Selector & Target Grade Selector */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Select Course
            </label>
            <select
              value={selectedCode}
              onChange={(e) => setSelectedCode(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            >
              {eligibleCourses.map(c => (
                <option key={c.course_code} value={c.course_code}>
                  {c.course_code}: {c.course_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Desired Target Letter Grade
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5">
              {Object.keys(targetPercentageMap).map(grade => (
                <button
                  key={grade}
                  onClick={() => setTargetGrade(grade)}
                  className={`py-2 text-xs font-bold rounded-lg border transition ${
                    targetGrade === grade
                      ? 'bg-blue-600 text-white border-blue-600 shadow'
                      : 'bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {grade}
                  <span className="block text-[10px] font-normal opacity-80">
                    {targetPercentageMap[grade]}%
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Solver Output Card */}
        {calc && whatIfResult && (
          <div className="mt-8 bg-slate-50 dark:bg-slate-900/60 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
              <Calculator className="w-4 h-4 text-blue-600" />
              Target Analysis: {selectedCourse?.course_code} for Grade {targetGrade} ({targetPct}%)
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                <span className="text-[10px] font-bold uppercase text-slate-400">Current Earned Weight</span>
                <div className="text-xl font-bold text-slate-800 dark:text-slate-200">
                  {calc.earned_weight.toFixed(2)}%
                </div>
                <span className="text-[11px] text-slate-500">out of {calc.completed_weight.toFixed(1)}% graded</span>
              </div>

              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                <span className="text-[10px] font-bold uppercase text-slate-400">Remaining Weight</span>
                <div className="text-xl font-bold text-slate-800 dark:text-slate-200">
                  {whatIfResult.remainingWeight.toFixed(1)}%
                </div>
                <span className="text-[11px] text-slate-500">unsubmitted points</span>
              </div>

              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                <span className="text-[10px] font-bold uppercase text-blue-600 dark:text-blue-400">Required Avg on Remaining</span>
                <div className="text-xl font-black text-blue-600 dark:text-blue-400">
                  {whatIfResult.requiredAvg > 0 ? `${whatIfResult.requiredAvg}%` : '0%'}
                </div>
                <span className="text-[11px] text-slate-500">to achieve {targetGrade}</span>
              </div>

              <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                <span className="text-[10px] font-bold uppercase text-slate-400">Feasibility</span>
                <div className="mt-1">
                  <span className={`inline-block px-2.5 py-1 text-xs font-bold rounded-full ${
                    whatIfResult.feasibility === 'Secured'
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                      : whatIfResult.feasibility === 'Achievable'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                      : whatIfResult.feasibility === 'Challenging'
                      ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                      : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                  }`}>
                    {whatIfResult.feasibility}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400">
                  {whatIfResult.feasibility === 'Impossible' ? 'Requires > 100%' : 'Mathematically possible'}
                </span>
              </div>
            </div>

            {/* Interactive Slider */}
            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Simulate Hypothetical Average on Remaining Assessments:
                </span>
                <span className="text-sm font-mono font-bold text-blue-600 dark:text-blue-400">
                  {hypotheticalRemainingScore}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={hypotheticalRemainingScore}
                onChange={(e) => setHypotheticalRemainingScore(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="mt-3 flex items-center justify-between p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 text-xs">
                <span>
                  If you average <strong className="text-blue-600">{hypotheticalRemainingScore}%</strong> on remaining tasks:
                </span>
                <span className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  Final Score: <span className="font-mono text-emerald-600">{hypotheticalFinal.toFixed(1)}%</span>
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 rounded font-black">
                    {hypotheticalLetter}
                  </span>
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
