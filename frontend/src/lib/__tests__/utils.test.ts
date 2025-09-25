import { describe, it, expect } from 'vitest'
import { cn } from '../utils'

describe('utils', () => {
  describe('cn (classname utility)', () => {
    it('should merge classes correctly', () => {
      const result = cn('text-red-500', 'bg-blue-500')
      expect(result).toBe('text-red-500 bg-blue-500')
    })

    it('should handle conditional classes', () => {
      const isActive = false
      const isVisible = true
      const result = cn('text-red-500', isActive && 'bg-blue-500', isVisible && 'p-4')
      expect(result).toBe('text-red-500 p-4')
    })

    it('should handle undefined and null values', () => {
      const result = cn('text-red-500', undefined, null, 'p-4')
      expect(result).toBe('text-red-500 p-4')
    })

    it('should handle empty input', () => {
      const result = cn()
      expect(result).toBe('')
    })

    it('should merge conflicting Tailwind classes correctly', () => {
      // This test assumes tailwind-merge is working correctly
      const result = cn('text-red-500', 'text-blue-500')
      expect(result).toBe('text-blue-500')
    })
  })
})