import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserManualAssistant } from './user-manual-assistant';

describe('UserManuals', () => {
  let component: UserManualAssistant;
  let fixture: ComponentFixture<UserManualAssistant>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserManualAssistant]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserManualAssistant);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
