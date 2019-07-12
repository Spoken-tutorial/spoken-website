import { Component, OnInit, Input } from '@angular/core';
import { TutorialsService } from '../../_service/tutorials.service'
import { Router } from '@angular/router';

@Component({
  selector: 'app-tutorials',
  templateUrl: './tutorials.component.html',
  styleUrls: ['./tutorials.component.sass']
})
export class TutorialsComponent implements OnInit {

  @Input() tutorial: any;

  constructor(public tutorialService: TutorialsService,
    public router: Router) { }

  public onClickCreate(){
    this.router.navigate(['ScriptCreateComponent']);
  }

  ngOnInit() {
  }

}
