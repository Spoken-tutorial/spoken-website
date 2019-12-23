import { TestBed } from '@angular/core/testing';

import { FossService } from './foss.service';

describe('FossService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: FossService = TestBed.get(FossService);
    expect(service).toBeTruthy();
  });
});
