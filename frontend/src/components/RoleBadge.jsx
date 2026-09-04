import React from 'react';

const roleStyles = {
  ADMINISTRATOR: {
    bg: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    dot: 'bg-rose-400',
    label: 'Administrator',
  },
  MANAGER: {
    bg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    dot: 'bg-amber-400',
    label: 'Manager',
  },
  REVIEWER: {
    bg: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
    dot: 'bg-indigo-400',
    label: 'Reviewer',
  },
  EMPLOYEE: {
    bg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    dot: 'bg-emerald-400',
    label: 'Employee',
  },
};

export const RoleBadge = ({ role, size = 'md' }) => {
  const style = roleStyles[role] || {
    bg: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
    dot: 'bg-slate-400',
    label: role || 'Unknown',
  };

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${style.bg} ${sizeClasses} shadow-sm transition-all`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot} animate-pulse`} />
      {style.label}
    </span>
  );
};
