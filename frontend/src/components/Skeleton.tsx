'use client';

export function ProductSkeleton() {
  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl overflow-hidden animate-pulse">
      <div className="h-48 bg-dark-700" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-dark-700 rounded w-3/4" />
        <div className="h-4 bg-dark-700 rounded w-1/2" />
        <div className="h-6 bg-dark-700 rounded w-1/3 mt-4" />
      </div>
    </div>
  );
}

export function OfferSkeleton() {
  return (
    <div className="flex items-center gap-4 p-4 bg-dark-800 border border-dark-700 rounded-xl animate-pulse">
      <div className="w-24 h-8 bg-dark-700 rounded-full" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-dark-700 rounded w-1/3" />
        <div className="h-3 bg-dark-700 rounded w-1/4" />
      </div>
      <div className="w-20 space-y-2">
        <div className="h-6 bg-dark-700 rounded" />
        <div className="h-3 bg-dark-700 rounded" />
      </div>
      <div className="w-14 h-14 bg-dark-700 rounded-xl" />
      <div className="w-24 h-10 bg-dark-700 rounded-lg" />
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-6 bg-dark-800 border border-dark-700 rounded-xl animate-pulse">
            <div className="h-4 bg-dark-700 rounded w-1/2 mb-3" />
            <div className="h-8 bg-dark-700 rounded w-1/3" />
          </div>
        ))}
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-20 bg-dark-800 border border-dark-700 rounded-xl animate-pulse" />
      ))}
    </div>
  );
}
