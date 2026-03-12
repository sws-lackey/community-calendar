import React from 'react';
import EventCard from './EventCard.jsx';

export default function UniformGrid({ events, filterTerm, onCategoryFilter, variant, columnCount }) {
  if (!events || !events.length) return null;

  const cols = variant === 'gridcompact' ? Math.max(columnCount, 2) : columnCount;

  return (
    <div
      className="grid w-full gap-4"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
    >
      {events.map(event => (
        <EventCard
          key={event.id}
          event={event}
          filterTerm={filterTerm}
          onCategoryFilter={onCategoryFilter}
          variant={variant}
        />
      ))}
    </div>
  );
}
