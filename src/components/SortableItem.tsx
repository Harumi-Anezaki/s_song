import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface SortableItemProps {
  id: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export const SortableItem: React.FC<SortableItemProps> = ({ id, children, style, className }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const combinedStyle = {
    ...style,
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={combinedStyle} {...attributes} {...listeners} className={className}>
      {children}
    </div>
  );
};
