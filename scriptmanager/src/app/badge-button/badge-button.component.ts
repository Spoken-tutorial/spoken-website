import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-badge-button',
  templateUrl: './badge-button.component.html',
  styleUrls: ['./badge-button.component.sass']
})
export class BadgeButtonComponent implements OnInit {
  @Input() faClass: string;
  @Input() textClass: string;
  @Input() text: string;
  @Input() textTooltip: string;

  constructor() { }

  ngOnInit() {
  }

}
